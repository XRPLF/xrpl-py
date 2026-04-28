"""
High-level transaction builders for confidential MPT transactions.

This module provides convenient functions to prepare confidential MPT transactions
using the C bindings (xrpl.core.confidential). Each function handles the
complexity of proof generation, encryption, and transaction construction.

Design principles (matching the mpt-crypto C library pattern):
- All cryptographic keys are explicit parameters — the caller provides them.
- The builders only query the ledger for mutable account state that the caller
  cannot know in advance (sequence number, encrypted balance, version counter).
- Blinding factors are generated using mpt_generate_blinding_factor (validates
  the scalar against the secp256k1 curve order), not raw random bytes.
"""

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
    from xrpl.core.confidential.crypto_bindings import ffi, lib

    # Global MPTCrypto instance used by all transaction builder functions
    crypto = MPTCrypto()
except ImportError:
    crypto = None  # type: ignore
    ffi = None  # type: ignore
    lib = None  # type: ignore


def _generate_blinding_factor() -> str:
    """
    Generate a cryptographically valid blinding factor using mpt_generate_blinding_factor.

    Unlike secrets.token_bytes(32), this function validates the scalar against
    the secp256k1 curve order, ensuring it is a valid private key / blinding factor.

    Returns:
        64-char hex string (32-byte blinding factor)
    """
    bf = ffi.new("uint8_t[32]")
    result = lib.mpt_generate_blinding_factor(bf)
    if result != 0:
        raise RuntimeError("Failed to generate blinding factor")
    return bytes(bf[0:32]).hex().upper()


def prepare_confidential_convert(
    client: Client,
    wallet: Wallet,
    mpt_issuance_id: str,
    amount: int,
    issuer_pubkey: str,
    holder_privkey: Optional[str] = None,
    holder_pubkey: Optional[str] = None,
    auditor_pubkey: Optional[str] = None,
) -> ConfidentialMPTConvert:
    """
    Prepare a ConfidentialMPTConvert transaction (public -> confidential).

    This function:
    1. Queries the ledger for account sequence
    2. Generates holder keypair if not provided
    3. Computes context hash
    4. Generates Schnorr proof of knowledge
    5. Encrypts amount for holder, issuer, and auditor (if present)
    6. Creates the transaction object

    Args:
        client: XRPL client (used to query account sequence)
        wallet: Wallet of the account converting tokens
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)
        amount: Amount to convert (uint64)
        issuer_pubkey: 66-char hex string of issuer's compressed public key
        holder_privkey: Optional 64-char hex string of holder's private key.
                       If not provided, a new keypair is generated.
        holder_pubkey: Optional 66-char hex string of holder's compressed public key.
                      If not provided, a new keypair is generated.
        auditor_pubkey: Optional 66-char hex string of auditor's compressed public key.
                       None means no auditor on this issuance.

    Returns:
        ConfidentialMPTConvert transaction ready to sign and submit
    """
    # Get account sequence (needed for context hash computation)
    account_info = client.request(AccountInfo(account=wallet.address))
    sequence = account_info.result["account_data"]["Sequence"]

    # Generate holder keypair if not provided
    if holder_privkey is None or holder_pubkey is None:
        holder_privkey, holder_pubkey = crypto.generate_keypair()

    # Compute context hash
    mpt_issuance_id_bytes = bytes.fromhex(mpt_issuance_id)
    context_id = compute_convert_context_hash(
        wallet.classic_address, sequence, mpt_issuance_id_bytes
    )

    # Generate Schnorr proof of knowledge
    schnorr_proof = crypto.generate_pok(holder_privkey, holder_pubkey, context_id)

    # Generate blinding factor (validated against curve order)
    blinding_factor = _generate_blinding_factor()

    # Encrypt amount for holder
    holder_c1, holder_c2, _ = crypto.encrypt(holder_pubkey, amount, blinding_factor)

    # Encrypt amount for issuer (same blinding factor)
    issuer_c1, issuer_c2, _ = crypto.encrypt(issuer_pubkey, amount, blinding_factor)

    # Encrypt amount for auditor if present (same blinding factor)
    auditor_encrypted_amount = None
    if auditor_pubkey:
        auditor_c1, auditor_c2, _ = crypto.encrypt(
            auditor_pubkey, amount, blinding_factor
        )
        auditor_encrypted_amount = auditor_c1 + auditor_c2

    return ConfidentialMPTConvert(
        account=wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
        mpt_amount=amount,
        holder_encryption_key=holder_pubkey,
        holder_encrypted_amount=holder_c1 + holder_c2,
        issuer_encrypted_amount=issuer_c1 + issuer_c2,
        blinding_factor=blinding_factor,
        zk_proof=schnorr_proof,
        auditor_encrypted_amount=auditor_encrypted_amount,
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
    receiver_pubkey: str,
    issuer_pubkey: str,
    auditor_pubkey: Optional[str] = None,
) -> ConfidentialMPTSend:
    """
    Prepare a ConfidentialMPTSend transaction (confidential transfer).

    This function:
    1. Queries ledger for sender's current balance, version, and sequence
    2. Computes context hash using sender's ConfidentialBalanceVersion
    3. Encrypts amount for sender, receiver, issuer, and auditor (if present)
    4. Creates Pedersen commitments for amount and current balance
    5. Generates compact AND-composed sigma proof + double bulletproof
    6. Constructs the transaction

    Args:
        client: XRPL client (used to query account sequence, balance, version)
        sender_wallet: Wallet of the sender
        receiver_address: Address of the receiver
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)
        amount: Amount to send (uint64)
        sender_privkey: 64-char hex string of sender's private key
        sender_pubkey: 66-char hex string of sender's compressed public key
        receiver_pubkey: 66-char hex string of receiver's compressed public key
        issuer_pubkey: 66-char hex string of issuer's compressed public key
        auditor_pubkey: Optional 66-char hex string of auditor's compressed public key.
                       None means no auditor on this issuance.

    Returns:
        ConfidentialMPTSend transaction ready to sign and submit
    """
    # Get sender's account info (sequence for context hash)
    account_info = client.request(AccountInfo(account=sender_wallet.address))
    sender_sequence = account_info.result["account_data"]["Sequence"]

    # Get sender's MPToken state (balance + version from ledger)
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

    # Compute context hash
    mpt_issuance_id_bytes = bytes.fromhex(mpt_issuance_id)
    context_id = compute_send_context_hash(
        sender_wallet.classic_address,
        sender_sequence,
        mpt_issuance_id_bytes,
        receiver_address,
        sender_version,
    )

    # Generate blinding factors (validated against curve order)
    amount_blinding = _generate_blinding_factor()
    balance_blinding = _generate_blinding_factor()

    # Encrypt amount for all parties (same blinding factor)
    sender_amount_c1, sender_amount_c2, _ = crypto.encrypt(
        sender_pubkey, amount, amount_blinding
    )
    receiver_amount_c1, receiver_amount_c2, _ = crypto.encrypt(
        receiver_pubkey, amount, amount_blinding
    )
    issuer_amount_c1, issuer_amount_c2, _ = crypto.encrypt(
        issuer_pubkey, amount, amount_blinding
    )

    # Encrypt amount for auditor if present
    auditor_encrypted_amount = None
    if auditor_pubkey:
        auditor_c1, auditor_c2, _ = crypto.encrypt(
            auditor_pubkey, amount, amount_blinding
        )
        auditor_encrypted_amount = auditor_c1 + auditor_c2

    # Create Pedersen commitments
    amount_commitment = crypto.create_pedersen_commitment(amount, amount_blinding)

    # Balance commitment is for the CURRENT balance (before the send)
    balance_commitment = crypto.create_pedersen_commitment(
        sender_current_balance, balance_blinding
    )

    # CRITICAL: Use the encrypted balance FROM THE LEDGER for the balance proof.
    # The proof must link the ledger's existing ciphertext (homomorphically
    # updated through previous transactions) to the new balance commitment.
    sender_balance_encrypted_ledger = sender_balance_hex

    # Build participants list: sender, receiver, issuer, and optionally auditor
    # The ZK proof supports 3 or 4 participants (n_participants).
    participants = [
        (sender_pubkey, sender_amount_c1 + sender_amount_c2),
        (receiver_pubkey, receiver_amount_c1 + receiver_amount_c2),
        (issuer_pubkey, issuer_amount_c1 + issuer_amount_c2),
    ]
    if auditor_pubkey:
        participants.append((auditor_pubkey, auditor_encrypted_amount))

    # Generate complete ZKProof using utility layer
    # Compact AND-composed sigma proof (192 bytes) + double bulletproof (754 bytes)
    zk_proof = crypto.create_confidential_send_proof(
        sender_privkey=sender_privkey,
        sender_pubkey=sender_pubkey,
        amount=amount,
        sender_current_balance=sender_current_balance,
        participants=participants,
        tx_blinding_factor=amount_blinding,
        context_hash=context_id,
        amount_commitment=amount_commitment,
        balance_commitment=balance_commitment,
        balance_blinding=balance_blinding,
        sender_balance_encrypted=sender_balance_encrypted_ledger,
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
        auditor_encrypted_amount=auditor_encrypted_amount,
    )


def prepare_confidential_convert_back(
    client: Client,
    wallet: Wallet,
    mpt_issuance_id: str,
    amount: int,
    holder_privkey: str,
    holder_pubkey: str,
    issuer_pubkey: str,
    auditor_pubkey: Optional[str] = None,
) -> ConfidentialMPTConvertBack:
    """
    Prepare a ConfidentialMPTConvertBack transaction (confidential -> public).

    This function:
    1. Queries ledger for holder's current balance, version, and sequence
    2. Computes context hash using holder's ConfidentialBalanceVersion
    3. Encrypts amount for holder, issuer, and auditor (if present)
    4. Creates Pedersen commitment for current balance
    5. Generates compact sigma proof + bulletproof
    6. Constructs the transaction

    Args:
        client: XRPL client (used to query account sequence, balance, version)
        wallet: Wallet of the account converting back
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)
        amount: Amount to convert back (uint64)
        holder_privkey: 64-char hex string of holder's private key
        holder_pubkey: 66-char hex string of holder's compressed public key
        issuer_pubkey: 66-char hex string of issuer's compressed public key
        auditor_pubkey: Optional 66-char hex string of auditor's compressed public key.
                       None means no auditor on this issuance.

    Returns:
        ConfidentialMPTConvertBack transaction ready to sign and submit
    """
    # Get account info (sequence for context hash)
    account_info = client.request(AccountInfo(account=wallet.address))
    sequence = account_info.result["account_data"]["Sequence"]

    # Get holder's MPToken state (balance + version from ledger)
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

    # Compute context hash
    mpt_issuance_id_bytes = bytes.fromhex(mpt_issuance_id)
    context_id = compute_convert_back_context_hash(
        wallet.classic_address,
        sequence,
        mpt_issuance_id_bytes,
        holder_version,
    )

    # Generate blinding factors (validated against curve order)
    amount_blinding = _generate_blinding_factor()
    balance_blinding = _generate_blinding_factor()

    # Encrypt amount for holder and issuer (same blinding factor)
    holder_c1, holder_c2, _ = crypto.encrypt(holder_pubkey, amount, amount_blinding)
    issuer_c1, issuer_c2, _ = crypto.encrypt(issuer_pubkey, amount, amount_blinding)

    # Encrypt amount for auditor if present
    auditor_encrypted_amount = None
    if auditor_pubkey:
        auditor_c1, auditor_c2, _ = crypto.encrypt(
            auditor_pubkey, amount, amount_blinding
        )
        auditor_encrypted_amount = auditor_c1 + auditor_c2

    # Create Pedersen commitment for current balance
    balance_commitment = crypto.create_pedersen_commitment(
        holder_current_balance, balance_blinding
    )

    # Generate compact sigma proof + bulletproof using utility layer
    # Total proof size: 816 bytes (128 compact sigma + 688 bulletproof)
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
        auditor_encrypted_amount=auditor_encrypted_amount,
    )


def prepare_confidential_clawback(
    client: Client,
    issuer_wallet: Wallet,
    holder_address: str,
    mpt_issuance_id: str,
    amount: int,
    issuer_privkey: str,
    issuer_pubkey: str,
    issuer_encrypted_balance: str,
) -> ConfidentialMPTClawback:
    """
    Prepare a ConfidentialMPTClawback transaction.

    This proves the issuer knows their confidential private key and that the
    encrypted balance matches the plaintext amount being clawed back.

    Args:
        client: XRPL client (used to query account sequence)
        issuer_wallet: Wallet of the issuer (must be the MPT issuer)
        holder_address: Address of the holder to claw back from
        mpt_issuance_id: 24-byte MPT issuance ID (hex string)
        amount: Amount to claw back (uint64)
        issuer_privkey: 64-char hex string of issuer's confidential private key
        issuer_pubkey: 66-char hex string of issuer's compressed public key
        issuer_encrypted_balance: 132-char hex string of the IssuerEncryptedBalance
                                 from the holder's MPToken on the ledger

    Returns:
        ConfidentialMPTClawback transaction ready to sign and submit
    """
    # Get issuer's sequence number (needed for context hash)
    issuer_info = client.request(AccountInfo(account=issuer_wallet.address))
    if issuer_info.is_successful() is False:
        raise ValueError(f"Failed to get issuer account info: {issuer_info.result}")
    issuer_sequence = issuer_info.result["account_data"]["Sequence"]

    # Compute context hash
    mpt_issuance_id_bytes = bytes.fromhex(mpt_issuance_id)
    context_id = compute_clawback_context_hash(
        issuer=issuer_wallet.address,
        sequence=issuer_sequence,
        mpt_issuance_id=mpt_issuance_id_bytes,
        holder=holder_address,
    )

    # Generate compact sigma proof
    clawback_proof = crypto.create_confidential_clawback_proof(
        issuer_privkey=issuer_privkey,
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
        zk_proof=clawback_proof,
    )
