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
        holder_pubkey: Optional 66-char hex string of holder's compressed public key
        issuer_pubkey: Optional 66-char hex string of issuer's compressed public key

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
    context_id = compute_convert_context_hash(
        wallet.classic_address, sequence, mpt_issuance_id_bytes, amount
    )

    # Generate Schnorr proof of knowledge
    # Note: generate_pok expects compressed public key (66 hex chars)
    schnorr_proof = crypto.generate_pok(holder_privkey, holder_pubkey, context_id)

    # Encrypt amount for holder
    # Note: encrypt expects compressed public key (66 hex chars)
    holder_c1, holder_c2, blinding_factor = crypto.encrypt(holder_pubkey, amount)

    # Encrypt amount for issuer
    issuer_c1, issuer_c2, _ = crypto.encrypt(issuer_pubkey, amount, blinding_factor)

    # Construct transaction
    # Note: holder_pubkey is already compressed (33 bytes = 66 hex chars)
    return ConfidentialMPTConvert(
        account=wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
        mpt_amount=amount,
        holder_elgamal_public_key=holder_pubkey,
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
        sender_pubkey: 66-char hex string of sender's compressed public key
        receiver_pubkey: Optional 66-char hex string of receiver's compressed public key
        issuer_pubkey: Optional 66-char hex string of issuer's compressed public key

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

    # Verify sender's public key matches ledger
    ledger_sender_pubkey = sender_mptoken.result["node"].get("ElGamalPublicKey", "")
    if ledger_sender_pubkey and ledger_sender_pubkey != sender_pubkey:
        raise ValueError(
            f"Sender public key mismatch: provided {sender_pubkey}, "
            f"ledger has {ledger_sender_pubkey}"
        )

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
    context_id = compute_send_context_hash(
        sender_wallet.classic_address,
        sender_sequence,
        mpt_issuance_id_bytes,
        receiver_address,
        sender_version,
    )

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
    # Note: create_pedersen_commitment returns compressed commitment (66 hex chars)
    amount_commitment = crypto.create_pedersen_commitment(amount, amount_blinding)

    # Balance commitment is for the CURRENT balance (before the send)
    # The verifier will compute PC_rem = PC_balance - PC_amount to get the remaining balance commitment
    balance_commitment = crypto.create_pedersen_commitment(
        sender_current_balance, balance_blinding
    )

    # CRITICAL: Use the encrypted balance FROM THE LEDGER for the balance linkage proof
    # DO NOT create a fresh encryption! The balance linkage proof must link the
    # ledger's existing ciphertext (which has been homomorphically updated through
    # previous transactions) to the new balance commitment.
    # The ledger value was already retrieved above as sender_balance_hex
    sender_balance_encrypted_ledger = sender_balance_hex  # 132 hex chars (66 bytes)

    # Generate complete ZKProof using utility layer
    # This includes: equality proof + linkage proofs + bulletproof
    recipients = [
        (sender_pubkey, sender_amount_c1 + sender_amount_c2),
        (receiver_pubkey, receiver_amount_c1 + receiver_amount_c2),
        (issuer_pubkey, issuer_amount_c1 + issuer_amount_c2),
    ]

    zk_proof = crypto.create_confidential_send_proof(
        sender_privkey=sender_privkey,
        amount=amount,
        sender_current_balance=sender_current_balance,
        recipients=recipients,
        tx_blinding_factor=amount_blinding,
        context_hash=context_id,
        amount_commitment=amount_commitment,
        amount_blinding=amount_blinding,
        sender_encrypted_amount=sender_amount_c1 + sender_amount_c2,
        balance_commitment=balance_commitment,
        balance_blinding=balance_blinding,
        sender_balance_encrypted=sender_balance_encrypted_ledger,  # FROM LEDGER!
    )

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
        holder_pubkey: 66-char hex string of holder's compressed public key
        issuer_pubkey: Optional 66-char hex string of issuer's compressed public key

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
    context_id = compute_convert_back_context_hash(
        wallet.classic_address,
        sequence,
        mpt_issuance_id_bytes,
        amount,
        holder_version,
    )

    # Generate blinding factors
    amount_blinding = secrets.token_bytes(32).hex().upper()
    balance_blinding = secrets.token_bytes(32).hex().upper()

    # Encrypt amount for holder and issuer
    holder_c1, holder_c2, _ = crypto.encrypt(holder_pubkey, amount, amount_blinding)
    issuer_c1, issuer_c2, _ = crypto.encrypt(issuer_pubkey, amount, amount_blinding)

    # Create Pedersen commitment for current balance
    # Note: create_pedersen_commitment returns compressed commitment (66 hex chars)
    balance_commitment = crypto.create_pedersen_commitment(
        holder_current_balance, balance_blinding
    )

    # Generate balance link proof using utility layer
    # Note: The proof now includes a bulletproof (883 bytes total)
    balance_link_proof = crypto.create_confidential_convert_back_proof(
        holder_privkey=holder_privkey,
        holder_pubkey=holder_pubkey,
        amount=amount,
        current_balance=holder_current_balance,
        context_hash=context_id,
        balance_commitment=balance_commitment,
        balance_blinding=balance_blinding,
        holder_balance_encrypted=holder_balance_hex,
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
    issuer_confidential_private_key: str,
) -> ConfidentialMPTClawback:
    """
    Prepare a ConfidentialMPTClawback transaction.

    **IMPORTANT**: This function requires the issuer's confidential private key
    to generate the equality proof. The proof demonstrates that the issuer knows
    the private key corresponding to their confidential public key and that the
    encrypted balance matches the plaintext amount being clawed back.

    Args:
        client: XRPL client for ledger queries
        issuer_wallet: Wallet of the issuer (must be the MPT issuer)
        holder_address: Address of the holder to claw back from
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)
        amount: Amount to claw back (uint64)
        issuer_confidential_private_key: 64-char hex string of the issuer's
            confidential private key (32 bytes). This is the private key
            corresponding to the issuer's ElGamal public key.

    Returns:
        ConfidentialMPTClawback transaction ready to sign and submit

    Raises:
        ValueError: If holder has no confidential balance
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

    # Extract issuer's encrypted balance (IssuerEncryptedBalance field)
    # This is the mirror balance that the issuer can decrypt
    issuer_encrypted_balance = holder_balance_obj.get("IssuerEncryptedBalance")
    if not issuer_encrypted_balance:
        raise ValueError(
            f"Holder {holder_address} has no IssuerEncryptedBalance for MPT "
            f"{mpt_issuance_id}"
        )

    # Get issuer's public key from MPT issuance
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
    context_id = compute_clawback_context_hash(
        issuer=issuer_wallet.address,
        sequence=issuer_sequence,
        mpt_issuance_id=mpt_issuance_id_bytes,
        amount=amount,
        holder=holder_address,
    )

    # Create equality proof using utility layer
    # This proves the issuer knows their confidential private key and that
    # the IssuerEncryptedBalance matches the plaintext amount
    equality_proof = crypto.create_confidential_clawback_proof(
        issuer_privkey=issuer_confidential_private_key,
        issuer_pubkey=issuer_pubkey,
        amount=amount,
        context_hash=context_id,
        issuer_encrypted_balance=issuer_encrypted_balance,
    )

    return ConfidentialMPTClawback(
        account=issuer_wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
        mpt_amount=amount,
        holder=holder_address,
        zk_proof=equality_proof,
    )
