"""
High-level transaction builders for confidential MPT transactions.

This module provides convenient functions to prepare confidential MPT transactions
using the C bindings (xrpl.ext.confidential). Each function handles the
complexity of proof generation, encryption, and transaction construction.

Each builder comes in two flavors:
- ``prepare_confidential_*(client, ...)``      — synchronous (SyncClient)
- ``prepare_confidential_*_async(client, ...)`` — asynchronous (AsyncClient)

Both share the same pure (client-free) crypto assembly; only the ledger queries
differ. All cryptographic keys are explicit parameters — the caller provides
them. The builders only query the ledger for mutable state the caller cannot
know in advance (sequence, encrypted balance, version). The confidential fee
multiplier is applied by core xrpl-py autofill (keyed on transaction type), so
the builders leave the fee unset.
"""

from typing import Optional, Tuple

from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.clients.sync_client import SyncClient
from xrpl.ext.confidential.context import (
    compute_clawback_context_hash,
    compute_convert_back_context_hash,
    compute_convert_context_hash,
    compute_send_context_hash,
)
from xrpl.ext.confidential.encryption import DEFAULT_DECRYPT_RANGE_HIGH
from xrpl.models.requests import AccountInfo, LedgerEntry
from xrpl.models.requests.ledger_entry import MPToken
from xrpl.models.transactions import (
    ConfidentialMPTClawback,
    ConfidentialMPTConvert,
    ConfidentialMPTConvertBack,
    ConfidentialMPTMergeInbox,
    ConfidentialMPTSend,
)
from xrpl.wallet import Wallet

try:
    from xrpl.ext.confidential import MPTCrypto
    from xrpl.ext.confidential.crypto_bindings import ffi, lib

    # Global MPTCrypto instance used by all transaction builder functions
    crypto = MPTCrypto()
except ImportError:
    crypto = None  # type: ignore
    ffi = None  # type: ignore
    lib = None  # type: ignore


def _generate_blinding_factor() -> str:
    """
    Generate a cryptographically valid blinding factor.

    Uses mpt_generate_blinding_factor, which validates the scalar against the
    secp256k1 curve order (unlike raw random bytes).

    Returns:
        64-char hex string (32-byte blinding factor)
    """
    bf = ffi.new("uint8_t[32]")
    result = lib.mpt_generate_blinding_factor(bf)
    if result != 0:
        raise RuntimeError("Failed to generate blinding factor")
    return bytes(bf[0:32]).hex().upper()


# The confidential base-fee multiplier (rippled charges base_fee * (1 +
# kConfidentialFeeMultiplier) for ZK-proof verification) is applied by core
# xrpl-py autofill's fee calculation, keyed on the transaction type — the same
# place EscrowFinish/AccountDelete/Batch special fees live. The builders leave
# the fee unset so autofill computes it, matching xrpl.js and xrpl4j.


# ──────────────────────────────────────────────────────────────────────────────
# Ledger I/O helpers (sync + async). Private; kept thin so the sync/async pairs
# differ only in the await.
# ──────────────────────────────────────────────────────────────────────────────
def _range_high_from_node(node: dict) -> int:
    # Decryption cost is O(range_high - range_low), so bound as tightly as
    # possible — NOT the issuance's MaximumAmount (typically ~2^63). No single
    # confidential balance can exceed the ConfidentialOutstandingAmount (falling
    # back to OutstandingAmount).
    for field in ("ConfidentialOutstandingAmount", "OutstandingAmount"):
        value = node.get(field)
        if value is not None and int(value) > 0:
            return int(value)
    return DEFAULT_DECRYPT_RANGE_HIGH


def _account_sequence(client: SyncClient, address: str) -> int:
    resp = client.request(AccountInfo(account=address))
    return resp.result["account_data"]["Sequence"]


async def _account_sequence_async(client: AsyncClient, address: str) -> int:
    resp = await client.request(AccountInfo(account=address))
    return resp.result["account_data"]["Sequence"]


def _parse_mptoken(result: dict) -> Tuple[int, str]:
    node = result.get("node", {})
    version = node.get("ConfidentialBalanceVersion", 0)
    balance_hex = node.get("ConfidentialBalanceSpending", "")
    return version, balance_hex


def _holder_key_registered_from_node(result: dict) -> bool:
    # rippled records the holder's ElGamal key (sfHolderEncryptionKey) on the
    # MPToken at the first convert; a subsequent convert that re-sends the key
    # returns tecDUPLICATE. Absent node (MPToken not yet created) => unregistered.
    return bool(result.get("node", {}).get("HolderEncryptionKey"))


def _holder_key_registered(
    client: SyncClient, account: str, mpt_issuance_id: str
) -> bool:
    resp = client.request(
        LedgerEntry(mptoken=MPToken(account=account, mpt_issuance_id=mpt_issuance_id))
    )
    return _holder_key_registered_from_node(resp.result)


async def _holder_key_registered_async(
    client: AsyncClient, account: str, mpt_issuance_id: str
) -> bool:
    resp = await client.request(
        LedgerEntry(mptoken=MPToken(account=account, mpt_issuance_id=mpt_issuance_id))
    )
    return _holder_key_registered_from_node(resp.result)


def _mptoken_state(
    client: SyncClient, account: str, mpt_issuance_id: str
) -> Tuple[int, str]:
    resp = client.request(
        LedgerEntry(mptoken=MPToken(account=account, mpt_issuance_id=mpt_issuance_id))
    )
    return _parse_mptoken(resp.result)


async def _mptoken_state_async(
    client: AsyncClient, account: str, mpt_issuance_id: str
) -> Tuple[int, str]:
    resp = await client.request(
        LedgerEntry(mptoken=MPToken(account=account, mpt_issuance_id=mpt_issuance_id))
    )
    return _parse_mptoken(resp.result)


def _decrypt_range_high(client: SyncClient, mpt_issuance_id: str) -> int:
    resp = client.request(LedgerEntry(mpt_issuance=mpt_issuance_id))
    return _range_high_from_node(resp.result.get("node", {}))


async def _decrypt_range_high_async(client: AsyncClient, mpt_issuance_id: str) -> int:
    resp = await client.request(LedgerEntry(mpt_issuance=mpt_issuance_id))
    return _range_high_from_node(resp.result.get("node", {}))


# ──────────────────────────────────────────────────────────────────────────────
# Pure (client-free) crypto assembly. Shared by the sync + async public builders.
# ──────────────────────────────────────────────────────────────────────────────
def _assemble_convert(  # noqa: ANN
    account: str,
    mpt_issuance_id: str,
    amount: int,
    sequence: int,
    issuer_pubkey: str,
    holder_privkey: Optional[str],
    holder_pubkey: Optional[str],
    auditor_pubkey: Optional[str],
    holder_key_registered: bool,
) -> ConfidentialMPTConvert:
    if holder_pubkey is None:
        # Never auto-generate here: the public key is registered on-chain, but a
        # private key generated (and discarded) inside the builder would be
        # unrecoverable, permanently locking the resulting confidential balance.
        # The caller must generate a keypair with MPTCrypto.generate_keypair()
        # and persist the private key.
        raise ValueError(
            "holder_pubkey is required. Generate a keypair with "
            "MPTCrypto.generate_keypair() and retain the private key; it is "
            "needed to decrypt and spend the confidential balance."
        )

    # rippled records sfHolderEncryptionKey on the first convert (the opt-in) and
    # rejects a second registration with tecDUPLICATE. Include the key + PoK only
    # when it is not yet on the ledger; subsequent converts omit both.
    register_key = not holder_key_registered
    schnorr_proof = None
    if register_key:
        if holder_privkey is None:
            raise ValueError(
                "holder_privkey is required for the first convert (holder-key "
                "registration): it signs the proof of knowledge that opts the "
                "account into confidential MPT."
            )
        context_id = compute_convert_context_hash(
            account, sequence, bytes.fromhex(mpt_issuance_id)
        )
        schnorr_proof = crypto.generate_pok(holder_privkey, holder_pubkey, context_id)

    blinding_factor = _generate_blinding_factor()

    holder_c1, holder_c2, _ = crypto.encrypt(holder_pubkey, amount, blinding_factor)
    issuer_c1, issuer_c2, _ = crypto.encrypt(issuer_pubkey, amount, blinding_factor)

    auditor_encrypted_amount = None
    if auditor_pubkey:
        auditor_c1, auditor_c2, _ = crypto.encrypt(
            auditor_pubkey, amount, blinding_factor
        )
        auditor_encrypted_amount = auditor_c1 + auditor_c2

    return ConfidentialMPTConvert(
        account=account,
        mptoken_issuance_id=mpt_issuance_id,
        mpt_amount=amount,
        holder_encryption_key=holder_pubkey if register_key else None,
        holder_encrypted_amount=holder_c1 + holder_c2,
        issuer_encrypted_amount=issuer_c1 + issuer_c2,
        blinding_factor=blinding_factor,
        zk_proof=schnorr_proof,
        auditor_encrypted_amount=auditor_encrypted_amount,
        # Pin the sequence: the proof's context hash is bound to this exact
        # value, so autofill must not substitute a different one.
        sequence=sequence,
    )


def _assemble_send(  # noqa: ANN
    account: str,
    receiver_address: str,
    mpt_issuance_id: str,
    amount: int,
    sequence: int,
    version: int,
    balance_hex: str,
    range_high: int,
    sender_privkey: str,
    sender_pubkey: str,
    receiver_pubkey: str,
    issuer_pubkey: str,
    auditor_pubkey: Optional[str],
) -> ConfidentialMPTSend:
    if not balance_hex:
        raise ValueError("Sender has no confidential balance")

    current_balance = crypto.decrypt(
        sender_privkey, balance_hex[:66], balance_hex[66:132], 0, range_high
    )

    context_id = compute_send_context_hash(
        account, sequence, bytes.fromhex(mpt_issuance_id), receiver_address, version
    )

    amount_blinding = _generate_blinding_factor()
    balance_blinding = _generate_blinding_factor()

    sender_c1, sender_c2, _ = crypto.encrypt(sender_pubkey, amount, amount_blinding)
    receiver_c1, receiver_c2, _ = crypto.encrypt(
        receiver_pubkey, amount, amount_blinding
    )
    issuer_c1, issuer_c2, _ = crypto.encrypt(issuer_pubkey, amount, amount_blinding)

    auditor_encrypted_amount = None
    if auditor_pubkey:
        auditor_c1, auditor_c2, _ = crypto.encrypt(
            auditor_pubkey, amount, amount_blinding
        )
        auditor_encrypted_amount = auditor_c1 + auditor_c2

    amount_commitment = crypto.create_pedersen_commitment(amount, amount_blinding)
    balance_commitment = crypto.create_pedersen_commitment(
        current_balance, balance_blinding
    )

    participants = [
        (sender_pubkey, sender_c1 + sender_c2),
        (receiver_pubkey, receiver_c1 + receiver_c2),
        (issuer_pubkey, issuer_c1 + issuer_c2),
    ]
    if auditor_pubkey:
        participants.append((auditor_pubkey, auditor_encrypted_amount))

    zk_proof = crypto.create_confidential_send_proof(
        sender_privkey=sender_privkey,
        sender_pubkey=sender_pubkey,
        amount=amount,
        sender_current_balance=current_balance,
        participants=participants,
        tx_blinding_factor=amount_blinding,
        context_hash=context_id,
        amount_commitment=amount_commitment,
        balance_commitment=balance_commitment,
        balance_blinding=balance_blinding,
        # Link the ledger's existing (homomorphically-updated) ciphertext to the
        # new balance commitment.
        sender_balance_encrypted=balance_hex,
    )

    return ConfidentialMPTSend(
        account=account,
        destination=receiver_address,
        mptoken_issuance_id=mpt_issuance_id,
        sender_encrypted_amount=sender_c1 + sender_c2,
        destination_encrypted_amount=receiver_c1 + receiver_c2,
        issuer_encrypted_amount=issuer_c1 + issuer_c2,
        amount_commitment=amount_commitment,
        balance_commitment=balance_commitment,
        zk_proof=zk_proof,
        auditor_encrypted_amount=auditor_encrypted_amount,
        # Pin the sequence: the proof's context hash is bound to this exact
        # value, so autofill must not substitute a different one.
        sequence=sequence,
    )


def _assemble_convert_back(  # noqa: ANN
    account: str,
    mpt_issuance_id: str,
    amount: int,
    sequence: int,
    version: int,
    balance_hex: str,
    range_high: int,
    holder_privkey: str,
    holder_pubkey: str,
    issuer_pubkey: str,
    auditor_pubkey: Optional[str],
) -> ConfidentialMPTConvertBack:
    if not balance_hex:
        raise ValueError("Holder has no confidential balance")

    current_balance = crypto.decrypt(
        holder_privkey, balance_hex[:66], balance_hex[66:132], 0, range_high
    )

    context_id = compute_convert_back_context_hash(
        account, sequence, bytes.fromhex(mpt_issuance_id), version
    )

    amount_blinding = _generate_blinding_factor()
    balance_blinding = _generate_blinding_factor()

    holder_c1, holder_c2, _ = crypto.encrypt(holder_pubkey, amount, amount_blinding)
    issuer_c1, issuer_c2, _ = crypto.encrypt(issuer_pubkey, amount, amount_blinding)

    auditor_encrypted_amount = None
    if auditor_pubkey:
        auditor_c1, auditor_c2, _ = crypto.encrypt(
            auditor_pubkey, amount, amount_blinding
        )
        auditor_encrypted_amount = auditor_c1 + auditor_c2

    balance_commitment = crypto.create_pedersen_commitment(
        current_balance, balance_blinding
    )
    balance_link_proof = crypto.create_confidential_convert_back_proof(
        holder_privkey=holder_privkey,
        holder_pubkey=holder_pubkey,
        amount=amount,
        current_balance=current_balance,
        context_hash=context_id,
        balance_commitment=balance_commitment,
        balance_blinding=balance_blinding,
        holder_balance_encrypted=balance_hex,
    )

    return ConfidentialMPTConvertBack(
        account=account,
        mptoken_issuance_id=mpt_issuance_id,
        mpt_amount=amount,
        holder_encrypted_amount=holder_c1 + holder_c2,
        issuer_encrypted_amount=issuer_c1 + issuer_c2,
        blinding_factor=amount_blinding,
        balance_commitment=balance_commitment,
        zk_proof=balance_link_proof,
        auditor_encrypted_amount=auditor_encrypted_amount,
        # Pin the sequence: the proof's context hash is bound to this exact
        # value, so autofill must not substitute a different one.
        sequence=sequence,
    )


def _assemble_clawback(  # noqa: ANN
    account: str,
    holder_address: str,
    mpt_issuance_id: str,
    amount: int,
    sequence: int,
    issuer_privkey: str,
    issuer_pubkey: str,
    issuer_encrypted_balance: str,
) -> ConfidentialMPTClawback:
    context_id = compute_clawback_context_hash(
        issuer=account,
        sequence=sequence,
        mpt_issuance_id=bytes.fromhex(mpt_issuance_id),
        holder=holder_address,
    )
    clawback_proof = crypto.create_confidential_clawback_proof(
        issuer_privkey=issuer_privkey,
        issuer_pubkey=issuer_pubkey,
        amount=amount,
        context_hash=context_id,
        issuer_encrypted_balance=issuer_encrypted_balance,
    )
    return ConfidentialMPTClawback(
        account=account,
        mptoken_issuance_id=mpt_issuance_id,
        mpt_amount=amount,
        holder=holder_address,
        zk_proof=clawback_proof,
        # Pin the sequence: the proof's context hash is bound to this exact
        # value, so autofill must not substitute a different one.
        sequence=sequence,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Public builders — synchronous
# ──────────────────────────────────────────────────────────────────────────────
def prepare_confidential_convert(
    client: SyncClient,
    wallet: Wallet,
    mpt_issuance_id: str,
    amount: int,
    issuer_pubkey: str,
    holder_privkey: str,
    holder_pubkey: str,
    auditor_pubkey: Optional[str] = None,
) -> ConfidentialMPTConvert:
    """
    Prepare a ConfidentialMPTConvert transaction (public -> confidential).

    Args:
        client: XRPL client (used to query account sequence and base fee).
        wallet: Wallet of the account converting tokens.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).
        amount: Amount to convert (uint64).
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        holder_privkey: 64-char hex of the holder's private key. Generate a
            keypair with ``MPTCrypto.generate_keypair()`` and persist the private
            key: it is required to later decrypt and spend the confidential
            balance, and the builder never generates one for you.
        holder_pubkey: 66-char hex of the holder's compressed public key.
        auditor_pubkey: Optional 66-char hex of the auditor's public key.

    Returns:
        A ConfidentialMPTConvert transaction ready to sign and submit.
    """
    return _assemble_convert(
        wallet.address,
        mpt_issuance_id,
        amount,
        _account_sequence(client, wallet.address),
        issuer_pubkey,
        holder_privkey,
        holder_pubkey,
        auditor_pubkey,
        _holder_key_registered(client, wallet.classic_address, mpt_issuance_id),
    )


def prepare_confidential_merge_inbox(
    client: SyncClient,
    wallet: Wallet,
    mpt_issuance_id: str,
) -> ConfidentialMPTMergeInbox:
    """
    Prepare a ConfidentialMPTMergeInbox transaction.

    Merges the inbox balance into the spending balance. No proofs or encryption
    are needed.

    Args:
        client: XRPL client. Accepted for signature parity with the other
            builders; MergeInbox needs no ledger data and the fee is applied by
            autofill, so it is currently unused.
        wallet: Wallet of the account merging its inbox.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).

    Returns:
        A ConfidentialMPTMergeInbox transaction ready to sign and submit.
    """
    return ConfidentialMPTMergeInbox(
        account=wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
    )


def prepare_confidential_send(
    client: SyncClient,
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

    Args:
        client: XRPL client (used to query sequence, balance, version, fee).
        sender_wallet: Wallet of the sender.
        receiver_address: Address of the receiver.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).
        amount: Amount to send (uint64).
        sender_privkey: 64-char hex of the sender's private key.
        sender_pubkey: 66-char hex of the sender's compressed public key.
        receiver_pubkey: 66-char hex of the receiver's compressed public key.
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        auditor_pubkey: Optional 66-char hex of the auditor's public key.

    Returns:
        A ConfidentialMPTSend transaction ready to sign and submit.
    """
    version, balance_hex = _mptoken_state(
        client, sender_wallet.classic_address, mpt_issuance_id
    )
    return _assemble_send(
        sender_wallet.address,
        receiver_address,
        mpt_issuance_id,
        amount,
        _account_sequence(client, sender_wallet.address),
        version,
        balance_hex,
        _decrypt_range_high(client, mpt_issuance_id),
        sender_privkey,
        sender_pubkey,
        receiver_pubkey,
        issuer_pubkey,
        auditor_pubkey,
    )


def prepare_confidential_convert_back(
    client: SyncClient,
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

    Args:
        client: XRPL client (used to query sequence, balance, version, fee).
        wallet: Wallet of the account converting back.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).
        amount: Amount to convert back (uint64).
        holder_privkey: 64-char hex of the holder's private key.
        holder_pubkey: 66-char hex of the holder's compressed public key.
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        auditor_pubkey: Optional 66-char hex of the auditor's public key.

    Returns:
        A ConfidentialMPTConvertBack transaction ready to sign and submit.
    """
    version, balance_hex = _mptoken_state(
        client, wallet.classic_address, mpt_issuance_id
    )
    return _assemble_convert_back(
        wallet.address,
        mpt_issuance_id,
        amount,
        _account_sequence(client, wallet.address),
        version,
        balance_hex,
        _decrypt_range_high(client, mpt_issuance_id),
        holder_privkey,
        holder_pubkey,
        issuer_pubkey,
        auditor_pubkey,
    )


def prepare_confidential_clawback(
    client: SyncClient,
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

    Args:
        client: XRPL client (used to query issuer sequence and base fee).
        issuer_wallet: Wallet of the issuer (must be the MPT issuer).
        holder_address: Address of the holder to claw back from.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).
        amount: Amount to claw back (uint64).
        issuer_privkey: 64-char hex of the issuer's confidential private key.
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        issuer_encrypted_balance: 132-char hex of the IssuerEncryptedBalance
            from the holder's MPToken on the ledger.

    Returns:
        A ConfidentialMPTClawback transaction ready to sign and submit.
    """
    return _assemble_clawback(
        issuer_wallet.address,
        holder_address,
        mpt_issuance_id,
        amount,
        _account_sequence(client, issuer_wallet.address),
        issuer_privkey,
        issuer_pubkey,
        issuer_encrypted_balance,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Public builders — asynchronous
# ──────────────────────────────────────────────────────────────────────────────
async def prepare_confidential_convert_async(
    client: AsyncClient,
    wallet: Wallet,
    mpt_issuance_id: str,
    amount: int,
    issuer_pubkey: str,
    holder_privkey: str,
    holder_pubkey: str,
    auditor_pubkey: Optional[str] = None,
) -> ConfidentialMPTConvert:
    """
    Async variant of :func:`prepare_confidential_convert`.

    Args:
        client: Async XRPL client.
        wallet: Wallet of the account converting tokens.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).
        amount: Amount to convert (uint64).
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        holder_privkey: 64-char hex of the holder's private key. Generate a
            keypair with ``MPTCrypto.generate_keypair()`` and persist the private
            key: it is required to later decrypt and spend the confidential
            balance, and the builder never generates one for you.
        holder_pubkey: 66-char hex of the holder's compressed public key.
        auditor_pubkey: Optional 66-char hex of the auditor's public key.

    Returns:
        A ConfidentialMPTConvert transaction ready to sign and submit.
    """
    return _assemble_convert(
        wallet.address,
        mpt_issuance_id,
        amount,
        await _account_sequence_async(client, wallet.address),
        issuer_pubkey,
        holder_privkey,
        holder_pubkey,
        auditor_pubkey,
        await _holder_key_registered_async(
            client, wallet.classic_address, mpt_issuance_id
        ),
    )


async def prepare_confidential_merge_inbox_async(
    client: AsyncClient,
    wallet: Wallet,
    mpt_issuance_id: str,
) -> ConfidentialMPTMergeInbox:
    """
    Async variant of :func:`prepare_confidential_merge_inbox`.

    Args:
        client: Async XRPL client.
        wallet: Wallet of the account merging its inbox.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).

    Returns:
        A ConfidentialMPTMergeInbox transaction ready to sign and submit.
    """
    return ConfidentialMPTMergeInbox(
        account=wallet.address,
        mptoken_issuance_id=mpt_issuance_id,
    )


async def prepare_confidential_send_async(
    client: AsyncClient,
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
    Async variant of :func:`prepare_confidential_send`.

    Args:
        client: Async XRPL client.
        sender_wallet: Wallet of the sender.
        receiver_address: Address of the receiver.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).
        amount: Amount to send (uint64).
        sender_privkey: 64-char hex of the sender's private key.
        sender_pubkey: 66-char hex of the sender's compressed public key.
        receiver_pubkey: 66-char hex of the receiver's compressed public key.
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        auditor_pubkey: Optional 66-char hex of the auditor's public key.

    Returns:
        A ConfidentialMPTSend transaction ready to sign and submit.
    """
    version, balance_hex = await _mptoken_state_async(
        client, sender_wallet.classic_address, mpt_issuance_id
    )
    return _assemble_send(
        sender_wallet.address,
        receiver_address,
        mpt_issuance_id,
        amount,
        await _account_sequence_async(client, sender_wallet.address),
        version,
        balance_hex,
        await _decrypt_range_high_async(client, mpt_issuance_id),
        sender_privkey,
        sender_pubkey,
        receiver_pubkey,
        issuer_pubkey,
        auditor_pubkey,
    )


async def prepare_confidential_convert_back_async(
    client: AsyncClient,
    wallet: Wallet,
    mpt_issuance_id: str,
    amount: int,
    holder_privkey: str,
    holder_pubkey: str,
    issuer_pubkey: str,
    auditor_pubkey: Optional[str] = None,
) -> ConfidentialMPTConvertBack:
    """
    Async variant of :func:`prepare_confidential_convert_back`.

    Args:
        client: Async XRPL client.
        wallet: Wallet of the account converting back.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).
        amount: Amount to convert back (uint64).
        holder_privkey: 64-char hex of the holder's private key.
        holder_pubkey: 66-char hex of the holder's compressed public key.
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        auditor_pubkey: Optional 66-char hex of the auditor's public key.

    Returns:
        A ConfidentialMPTConvertBack transaction ready to sign and submit.
    """
    version, balance_hex = await _mptoken_state_async(
        client, wallet.classic_address, mpt_issuance_id
    )
    return _assemble_convert_back(
        wallet.address,
        mpt_issuance_id,
        amount,
        await _account_sequence_async(client, wallet.address),
        version,
        balance_hex,
        await _decrypt_range_high_async(client, mpt_issuance_id),
        holder_privkey,
        holder_pubkey,
        issuer_pubkey,
        auditor_pubkey,
    )


async def prepare_confidential_clawback_async(
    client: AsyncClient,
    issuer_wallet: Wallet,
    holder_address: str,
    mpt_issuance_id: str,
    amount: int,
    issuer_privkey: str,
    issuer_pubkey: str,
    issuer_encrypted_balance: str,
) -> ConfidentialMPTClawback:
    """
    Async variant of :func:`prepare_confidential_clawback`.

    Args:
        client: Async XRPL client.
        issuer_wallet: Wallet of the issuer (must be the MPT issuer).
        holder_address: Address of the holder to claw back from.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string).
        amount: Amount to claw back (uint64).
        issuer_privkey: 64-char hex of the issuer's confidential private key.
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        issuer_encrypted_balance: 132-char hex of the IssuerEncryptedBalance
            from the holder's MPToken on the ledger.

    Returns:
        A ConfidentialMPTClawback transaction ready to sign and submit.
    """
    return _assemble_clawback(
        issuer_wallet.address,
        holder_address,
        mpt_issuance_id,
        amount,
        await _account_sequence_async(client, issuer_wallet.address),
        issuer_privkey,
        issuer_pubkey,
        issuer_encrypted_balance,
    )
