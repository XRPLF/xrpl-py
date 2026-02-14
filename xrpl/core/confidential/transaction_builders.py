"""
High-level transaction builders for confidential MPT transactions.

This module provides convenient functions to prepare confidential MPT transactions
using the C bindings (xrpl.core.confidential). Each function handles all the
complexity of proof generation, encryption, and transaction construction.
"""

import secrets
from typing import Optional

from xrpl.clients import Client
from xrpl.models.requests import AccountInfo, AccountObjects, LedgerEntry
from xrpl.models.requests.account_objects import AccountObjectType
from xrpl.models.requests.ledger_entry import MPToken
from xrpl.models.transactions import (
    ConfidentialMPTClawback,
    ConfidentialMPTConvert,
    ConfidentialMPTConvertBack,
    ConfidentialMPTMergeInbox,
    ConfidentialMPTSend,
)
from xrpl.wallet import Wallet

from .context import (
    compute_clawback_context_hash,
    compute_convert_back_context_hash,
    compute_convert_context_hash,
    compute_send_context_hash,
)
from .utils import reverse_coordinates

try:
    from xrpl.core.confidential import MPTCrypto

    # Global MPTCrypto instance used by all transaction builder functions
    crypto = MPTCrypto()
except ImportError:
    crypto = None  # type: ignore


def prepare_confidential_convert(
    client: Client,
    wallet: Wallet,
    mpt_issuance_id: str,
    amount: int,
    holder_privkey: Optional[str] = None,
    holder_pubkey: Optional[str] = None,
    issuer_pubkey: Optional[str] = None,
) -> ConfidentialMPTConvert:
    """
    Prepare a ConfidentialMPTConvert transaction (public → confidential).

    This function:
    1. Queries the ledger for account sequence and issuer public key
    2. Generates holder keypair if not provided
    3. Computes context hash
    4. Generates Schnorr proof of knowledge
    5. Encrypts amount for holder and issuer
    6. Creates the transaction object

    Args:
        client: XRPL client for ledger queries
        wallet: Wallet of the account converting tokens
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)
        amount: Amount to convert (uint64)
        holder_privkey: Optional 64-char hex string of holder's private key
        holder_pubkey: Optional 128-char hex string of holder's public key
        issuer_pubkey: Optional 128-char hex string of issuer's public key

    Returns:
        ConfidentialMPTConvert transaction ready to sign and submit
    """
    # Get account sequence
    account_info = client.request(AccountInfo(account=wallet.address))
    sequence = account_info.result["account_data"]["Sequence"]

    # Generate holder keypair if not provided
    if holder_privkey is None or holder_pubkey is None:
        holder_privkey, holder_pubkey = crypto.generate_keypair()

    # Get issuer public key if not provided
    if issuer_pubkey is None:
        # Query MPT issuance for issuer's public key
        mpt_issuance = client.request(
            LedgerEntry(
                mpt_issuance=mpt_issuance_id,
            )
        )
        issuer_pubkey = mpt_issuance.result["node"].get("IssuerElGamalPublicKey", "")
        if not issuer_pubkey:
            raise ValueError("Issuer ElGamal public key not found in MPT issuance")

    # Compute context hash
    mpt_issuance_id_bytes = bytes.fromhex(mpt_issuance_id)
    context_id_bytes = compute_convert_context_hash(
        wallet.classic_address, sequence, mpt_issuance_id_bytes, amount
    )
    context_id = context_id_bytes.hex().upper()

    # Generate Schnorr proof of knowledge
    schnorr_proof = crypto.generate_pok(holder_privkey, holder_pubkey, context_id)

    # Encrypt amount for holder
    holder_c1, holder_c2, blinding_factor = crypto.encrypt(holder_pubkey, amount)

    # Encrypt amount for issuer
    issuer_c1, issuer_c2, _ = crypto.encrypt(issuer_pubkey, amount, blinding_factor)

    # Reverse coordinates for rippled compatibility
    holder_pubkey_bytes = bytes.fromhex(holder_pubkey)
    holder_pubkey_reversed = reverse_coordinates(holder_pubkey_bytes)
    holder_pubkey_reversed_hex = holder_pubkey_reversed.hex().upper()

    # Construct transaction
    return ConfidentialMPTConvert(
        account=wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
        mpt_amount=amount,
        holder_elgamal_public_key=holder_pubkey_reversed_hex,
        holder_encrypted_amount=holder_c1 + holder_c2,
        issuer_encrypted_amount=issuer_c1 + issuer_c2,
        blinding_factor=blinding_factor,
        zk_proof=schnorr_proof,
    )


def prepare_confidential_merge_inbox(
    wallet: Wallet,
    mpt_issuance_id: str,
) -> ConfidentialMPTMergeInbox:
    """
    Prepare a ConfidentialMPTMergeInbox transaction.

    This is the simplest confidential transaction - it just merges the inbox
    balance to the spending balance. No proofs or encryption needed.

    Args:
        wallet: Wallet of the account merging inbox
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)

    Returns:
        ConfidentialMPTMergeInbox transaction ready to sign and submit
    """
    return ConfidentialMPTMergeInbox(
        account=wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
    )


def prepare_confidential_send(
    client: Client,
    sender_wallet: Wallet,
    receiver_address: str,
    mpt_issuance_id: str,
    amount: int,
    sender_privkey: str,
    sender_pubkey: str,
    receiver_pubkey: Optional[str] = None,
    issuer_pubkey: Optional[str] = None,
) -> ConfidentialMPTSend:
    """
    Prepare a ConfidentialMPTSend transaction (confidential transfer).

    This function:
    1. Queries ledger for sender's current balance, version, and sequence
    2. Queries receiver and issuer public keys if not provided
    3. Computes context hash using sender's ConfidentialBalanceVersion
    4. Encrypts amount for sender, receiver, and issuer
    5. Creates Pedersen commitments for amount and current balance
    6. Generates same plaintext proof (3 ciphertexts)
    7. Generates amount link proof
    8. Generates balance link proof
    9. Constructs the transaction

    Args:
        client: XRPL client for ledger queries
        sender_wallet: Wallet of the sender
        receiver_address: Address of the receiver
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)
        amount: Amount to send (uint64)
        sender_privkey: 64-char hex string of sender's private key
        sender_pubkey: 128-char hex string of sender's public key
        receiver_pubkey: Optional 128-char hex string of receiver's public key
        issuer_pubkey: Optional 128-char hex string of issuer's public key

    Returns:
        ConfidentialMPTSend transaction ready to sign and submit
    """
    # Get sender's account info
    account_info = client.request(AccountInfo(account=sender_wallet.address))
    sender_sequence = account_info.result["account_data"]["Sequence"]

    # Get sender's MPToken state
    sender_mptoken = client.request(
        LedgerEntry(
            mptoken=MPToken(
                account=sender_wallet.classic_address,
                mpt_issuance_id=mpt_issuance_id,
            )
        )
    )

    # Get sender's current balance and version
    sender_version = sender_mptoken.result.get("node", {}).get(
        "ConfidentialBalanceVersion", 0
    )
    sender_balance_hex = sender_mptoken.result["node"].get(
        "ConfidentialBalanceSpending", ""
    )
    if not sender_balance_hex:
        raise ValueError("Sender has no confidential balance")

    # Extract c1 and c2 as hex strings
    sender_balance_c1 = sender_balance_hex[:66]  # First 33 bytes = 66 hex chars
    sender_balance_c2 = sender_balance_hex[66:132]  # Next 33 bytes = 66 hex chars

    # Decrypt sender's current balance
    sender_current_balance = crypto.decrypt(
        sender_privkey, sender_balance_c1, sender_balance_c2
    )

    # Get receiver public key if not provided
    if receiver_pubkey is None:
        receiver_mptoken = client.request(
            LedgerEntry(
                mptoken=MPToken(
                    account=receiver_address,
                    mpt_issuance_id=mpt_issuance_id,
                )
            )
        )
        receiver_pubkey = receiver_mptoken.result["node"].get("ElGamalPublicKey", "")
        if not receiver_pubkey:
            raise ValueError("Receiver ElGamal public key not found")

    # Get issuer public key if not provided
    if issuer_pubkey is None:
        mpt_issuance = client.request(
            LedgerEntry(
                mpt_issuance=mpt_issuance_id,
            )
        )
        issuer_pubkey = mpt_issuance.result["node"].get("IssuerElGamalPublicKey", "")
        if not issuer_pubkey:
            raise ValueError("Issuer ElGamal public key not found")

    # Compute context hash
    mpt_issuance_id_bytes = bytes.fromhex(mpt_issuance_id)
    context_id_bytes = compute_send_context_hash(
        sender_wallet.classic_address,
        sender_sequence,
        mpt_issuance_id_bytes,
        receiver_address,
        sender_version,
    )
    context_id = context_id_bytes.hex().upper()

    # Generate blinding factors
    amount_blinding = secrets.token_bytes(32).hex().upper()
    balance_blinding = secrets.token_bytes(32).hex().upper()

    # Encrypt amount for all parties
    sender_amount_c1, sender_amount_c2, _ = crypto.encrypt(
        sender_pubkey, amount, amount_blinding
    )
    receiver_amount_c1, receiver_amount_c2, _ = crypto.encrypt(
        receiver_pubkey, amount, amount_blinding
    )
    issuer_amount_c1, issuer_amount_c2, _ = crypto.encrypt(
        issuer_pubkey, amount, amount_blinding
    )

    # Create Pedersen commitments
    amount_commitment_raw = crypto.create_pedersen_commitment(amount, amount_blinding)
    balance_commitment_raw = crypto.create_pedersen_commitment(
        sender_current_balance, balance_blinding
    )

    # Reverse coordinates for rippled compatibility
    amount_commitment_bytes = bytes.fromhex(amount_commitment_raw)
    balance_commitment_bytes = bytes.fromhex(balance_commitment_raw)
    amount_commitment = reverse_coordinates(amount_commitment_bytes).hex().upper()
    balance_commitment = reverse_coordinates(balance_commitment_bytes).hex().upper()

    # Generate proofs
    # 1. Same plaintext proof (3 ciphertexts encrypt same amount)
    ciphertexts = [
        (sender_amount_c1, sender_amount_c2, sender_pubkey, amount_blinding),
        (receiver_amount_c1, receiver_amount_c2, receiver_pubkey, amount_blinding),
        (issuer_amount_c1, issuer_amount_c2, issuer_pubkey, amount_blinding),
    ]
    same_plaintext_proof = crypto.create_same_plaintext_proof_multi(
        amount, ciphertexts, context_id
    )

    # 2. Amount link proof (normal parameter order)
    # Use non-reversed commitment for proof generation
    amount_link_proof = crypto.create_elgamal_pedersen_link_proof(
        sender_amount_c1,
        sender_amount_c2,
        sender_pubkey,
        amount_commitment_raw,  # Use non-reversed commitment
        amount,
        amount_blinding,
        amount_blinding,
        context_id,
    )

    # 3. Balance link proof
    # Use non-reversed commitment for proof generation
    balance_link_proof = crypto.create_balance_link_proof(
        sender_pubkey,
        sender_balance_c2,
        sender_balance_c1,
        balance_commitment_raw,
        sender_current_balance,
        sender_privkey,
        balance_blinding,
        context_id,
    )

    # Concatenate all proofs
    zk_proof = same_plaintext_proof + amount_link_proof + balance_link_proof

    # Construct transaction
    return ConfidentialMPTSend(
        account=sender_wallet.address,
        destination=receiver_address,
        mptoken_issuance_id=mpt_issuance_id,
        sender_encrypted_amount=sender_amount_c1 + sender_amount_c2,
        destination_encrypted_amount=receiver_amount_c1 + receiver_amount_c2,
        issuer_encrypted_amount=issuer_amount_c1 + issuer_amount_c2,
        amount_commitment=amount_commitment,
        balance_commitment=balance_commitment,
        zk_proof=zk_proof,
    )


def prepare_confidential_convert_back(
    client: Client,
    wallet: Wallet,
    mpt_issuance_id: str,
    amount: int,
    holder_privkey: str,
    holder_pubkey: str,
    issuer_pubkey: Optional[str] = None,
) -> ConfidentialMPTConvertBack:
    """
    Prepare a ConfidentialMPTConvertBack transaction (confidential → public).

    This function:
    1. Queries ledger for holder's current balance, version, and sequence
    2. Queries issuer public key if not provided
    3. Computes context hash using holder's ConfidentialBalanceVersion
    4. Encrypts amount for holder and issuer
    5. Creates Pedersen commitment for current balance
    6. Generates balance link proof
    7. Constructs the transaction

    Args:
        client: XRPL client for ledger queries
        wallet: Wallet of the account converting back
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)
        amount: Amount to convert back (uint64)
        holder_privkey: 64-char hex string of holder's private key
        holder_pubkey: 128-char hex string of holder's public key
        issuer_pubkey: Optional 128-char hex string of issuer's public key

    Returns:
        ConfidentialMPTConvertBack transaction ready to sign and submit
    """
    # Get account info
    account_info = client.request(AccountInfo(account=wallet.address))
    sequence = account_info.result["account_data"]["Sequence"]

    # Get holder's MPToken state
    holder_mptoken = client.request(
        LedgerEntry(
            mptoken=MPToken(
                account=wallet.classic_address,
                mpt_issuance_id=mpt_issuance_id,
            )
        )
    )

    # Get holder's current balance and version
    holder_version = holder_mptoken.result.get("node", {}).get(
        "ConfidentialBalanceVersion", 0
    )
    holder_balance_hex = holder_mptoken.result["node"].get(
        "ConfidentialBalanceSpending", ""
    )
    if not holder_balance_hex:
        raise ValueError("Holder has no confidential balance")

    # Extract c1 and c2 as hex strings
    holder_balance_c1 = holder_balance_hex[:66]  # First 33 bytes = 66 hex chars
    holder_balance_c2 = holder_balance_hex[66:132]  # Next 33 bytes = 66 hex chars

    # Decrypt holder's current balance
    holder_current_balance = crypto.decrypt(
        holder_privkey, holder_balance_c1, holder_balance_c2
    )

    # Get issuer public key if not provided
    if issuer_pubkey is None:
        mpt_issuance = client.request(
            LedgerEntry(
                mpt_issuance=mpt_issuance_id,
            )
        )
        issuer_pubkey = mpt_issuance.result["node"].get("IssuerElGamalPublicKey", "")
        if not issuer_pubkey:
            raise ValueError("Issuer ElGamal public key not found")

    # Compute context hash
    mpt_issuance_id_bytes = bytes.fromhex(mpt_issuance_id)
    context_id_bytes = compute_convert_back_context_hash(
        wallet.classic_address,
        sequence,
        mpt_issuance_id_bytes,
        amount,
        holder_version,
    )
    context_id = context_id_bytes.hex().upper()

    # Generate blinding factors
    amount_blinding = secrets.token_bytes(32).hex().upper()
    balance_blinding = secrets.token_bytes(32).hex().upper()

    # Encrypt amount for holder and issuer
    holder_c1, holder_c2, _ = crypto.encrypt(holder_pubkey, amount, amount_blinding)
    issuer_c1, issuer_c2, _ = crypto.encrypt(issuer_pubkey, amount, amount_blinding)

    # Create Pedersen commitment for current balance
    balance_commitment_raw = crypto.create_pedersen_commitment(
        holder_current_balance, balance_blinding
    )

    # Reverse coordinates for rippled compatibility
    balance_commitment_bytes = bytes.fromhex(balance_commitment_raw)
    balance_commitment = reverse_coordinates(balance_commitment_bytes).hex().upper()

    # Generate balance link proof
    # Use non-reversed commitment for proof generation
    balance_link_proof = crypto.create_balance_link_proof(
        holder_pubkey,
        holder_balance_c2,
        holder_balance_c1,
        balance_commitment_raw,
        holder_current_balance,
        holder_privkey,
        balance_blinding,
        context_id,
    )

    # Construct transaction
    return ConfidentialMPTConvertBack(
        account=wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
        mpt_amount=amount,
        holder_encrypted_amount=holder_c1 + holder_c2,
        issuer_encrypted_amount=issuer_c1 + issuer_c2,
        blinding_factor=amount_blinding,
        balance_commitment=balance_commitment,
        zk_proof=balance_link_proof,
    )


def prepare_confidential_clawback(
    client: Client,
    issuer_wallet: Wallet,
    holder_address: str,
    mpt_issuance_id: str,
    amount: int,
    holder_balance_blinding_factor: str,
) -> ConfidentialMPTClawback:
    """
    Prepare a ConfidentialMPTClawback transaction.

    **IMPORTANT**: This function requires the issuer to track blinding factors
    for all encrypted balances. The issuer must have stored the blinding factor
    that was used when the holder's balance was encrypted.

    This is a significant infrastructure requirement:
    - Blinding factors must be stored in a secure database
    - Keyed by (holder_address, mpt_issuance_id)
    - Must be kept synchronized with all balance updates

    Args:
        client: XRPL client for ledger queries
        issuer_wallet: Wallet of the issuer (must be the MPT issuer)
        holder_address: Address of the holder to claw back from
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)
        amount: Amount to claw back (uint64)
        holder_balance_blinding_factor: 64-char hex string of blinding factor
            used to encrypt the holder's balance. The issuer MUST have tracked
            this value.

    Returns:
        ConfidentialMPTClawback transaction ready to sign and submit

    Raises:
        ValueError: If holder has no confidential balance or if the blinding
            factor is incorrect
    """
    # Get issuer's sequence number
    issuer_info = client.request(AccountInfo(account=issuer_wallet.address))
    if issuer_info.is_successful() is False:
        raise ValueError(f"Failed to get issuer account info: {issuer_info.result}")
    issuer_sequence = issuer_info.result["account_data"]["Sequence"]

    # Query holder's confidential balance
    holder_balance_response = client.request(
        AccountObjects(
            account=holder_address,
            type=AccountObjectType.MPTOKEN,
        )
    )
    if holder_balance_response.is_successful() is False:
        raise ValueError(
            f"Failed to get holder balance: {holder_balance_response.result}"
        )

    # Find the specific MPT balance
    holder_balance_obj = None
    for obj in holder_balance_response.result.get("account_objects", []):
        if obj.get("MPTIssuanceID") == mpt_issuance_id:
            holder_balance_obj = obj
            break

    if holder_balance_obj is None:
        raise ValueError(
            f"Holder {holder_address} has no balance for MPT {mpt_issuance_id}"
        )

    # Extract encrypted balance (C1 || C2)
    confidential_balance = holder_balance_obj.get("ConfidentialBalance")
    if not confidential_balance:
        raise ValueError(
            f"Holder {holder_address} has no confidential balance for MPT "
            f"{mpt_issuance_id}"
        )

    # Parse encrypted balance as hex strings
    balance_c1 = confidential_balance[:128]  # First 64 bytes = 128 hex chars
    balance_c2 = confidential_balance[128:256]  # Next 64 bytes = 128 hex chars

    # Get holder's public key
    holder_info = client.request(AccountInfo(account=holder_address))
    if holder_info.is_successful() is False:
        raise ValueError(f"Failed to get holder account info: {holder_info.result}")
    holder_pubkey = holder_info.result["account_data"].get("ConfidentialPublicKey")
    if not holder_pubkey:
        raise ValueError(f"Holder {holder_address} has no confidential public key")

    # Compute context hash
    mpt_issuance_id_bytes = bytes.fromhex(mpt_issuance_id)
    context_id_bytes = compute_clawback_context_hash(
        issuer=issuer_wallet.address,
        sequence=issuer_sequence,
        mpt_issuance_id=mpt_issuance_id_bytes,
        amount=amount,
        holder=holder_address,
    )
    context_id = context_id_bytes.hex().upper()

    # Create equality proof
    # This proves the issuer knows the blinding factor for the holder's balance
    equality_proof = crypto.create_equality_plaintext_proof(
        holder_pubkey,
        balance_c2,
        balance_c1,
        amount,
        holder_balance_blinding_factor,
        context_id,
    )

    return ConfidentialMPTClawback(
        account=issuer_wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
        mpt_amount=amount,
        holder=holder_address,
        zk_proof=equality_proof,
    )
