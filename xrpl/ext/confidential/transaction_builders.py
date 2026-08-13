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

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from typing_extensions import Self

from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.clients.sync_client import SyncClient
from xrpl.ext.confidential.context import (
    compute_clawback_context_hash,
    compute_convert_back_context_hash,
    compute_convert_context_hash,
    compute_send_context_hash,
)
from xrpl.ext.confidential.encryption import DEFAULT_DECRYPT_RANGE_HIGH
from xrpl.ext.confidential.homomorphic import add_ciphertexts, subtract_ciphertexts
from xrpl.models.requests import AccountInfo, LedgerEntry
from xrpl.models.requests.ledger_entry import MPToken
from xrpl.models.transactions import (
    ConfidentialMPTClawback,
    ConfidentialMPTConvert,
    ConfidentialMPTConvertBack,
    ConfidentialMPTMergeInbox,
    ConfidentialMPTSend,
)
from xrpl.models.transactions.confidential_mpt_constants import CIPHERTEXT_LENGTH
from xrpl.wallet import Wallet

try:
    from xrpl.ext.confidential import MPTCrypto
    from xrpl.ext.confidential.crypto_bindings import ffi, lib

    # Global MPTCrypto instance used by all transaction builder functions
    crypto = MPTCrypto()
    _NATIVE_IMPORT_ERROR: Optional[ImportError] = None
except ImportError as error:
    crypto = None  # type: ignore
    ffi = None  # type: ignore
    lib = None  # type: ignore
    _NATIVE_IMPORT_ERROR = error


# ──────────────────────────────────────────────────────────────────────────────
# Batch operation specs for prepare_confidential_batch. Each describes one
# confidential inner transaction in a chain over a single (account, token); the
# builder threads the predicted CB_S/version through them in order. Only the
# three CB_S-affecting types belong in a chain: Send and ConvertBack debit the
# spending balance (and bump the version), and MergeInbox credits it from the
# inbox (and bumps the version). Convert (writes only the inbox) and Clawback
# (targets the holder) never prove against the account's CB_S/version, so they
# need no prediction — add them to the Batch as plain inner transactions.
# ──────────────────────────────────────────────────────────────────────────────
_PUBKEY_HEX_LEN = 66  # 33-byte compressed secp256k1 public key


@dataclass(frozen=True)
class ConfidentialSendOp:
    """A confidential transfer of ``amount`` to one receiver."""

    receiver_address: str
    receiver_pubkey: str
    amount: int

    def __post_init__(self: Self) -> None:
        """Validate the fields (called by dataclasses after __init__)."""
        # receiver_address and receiver_pubkey are both str and adjacent; a swap
        # would otherwise build a valid-looking op whose proof binds the wrong
        # key and only fails on-ledger. The pubkey is a 66-char hex compressed
        # key; an XRPL address never is, so this catches the swap early.
        if len(self.receiver_pubkey) != _PUBKEY_HEX_LEN:
            raise ValueError(
                "receiver_pubkey must be a "
                f"{_PUBKEY_HEX_LEN}-char hex compressed public key "
                "(did you swap receiver_address and receiver_pubkey?)"
            )
        if self.amount <= 0:
            raise ValueError("amount must be a positive integer")


@dataclass(frozen=True)
class ConfidentialConvertBackOp:
    """Convert ``amount`` of confidential balance back to public tokens."""

    amount: int

    def __post_init__(self: Self) -> None:
        """Validate the fields (called by dataclasses after __init__)."""
        if self.amount <= 0:
            raise ValueError("amount must be a positive integer")


@dataclass(frozen=True)
class ConfidentialMergeInboxOp:
    """Merge the inbox balance into the spending balance."""


ConfidentialBatchOp = Union[
    ConfidentialSendOp, ConfidentialConvertBackOp, ConfidentialMergeInboxOp
]


def _require_native() -> None:
    """Raise the actionable "install the add-on" error if the native mpt-crypto
    extension is unavailable.

    Without this, a caller lacking the native library would hit a cryptic
    ``AttributeError: 'NoneType' object has no attribute ...`` deep inside a
    builder (``crypto``/``lib`` are ``None``). Re-raises the original
    :class:`ImportError` from ``crypto_bindings`` — which already carries the
    ``pip install xrpl-py-confidential`` instructions — chained as the cause.

    Raises:
        ImportError: If the native mpt-crypto extension is not available.
    """
    if crypto is None:
        raise ImportError(
            "Confidential MPT proof generation requires the native mpt-crypto "
            "extension, which is not available. Install the add-on with:  "
            "pip install xrpl-py-confidential"
        ) from _NATIVE_IMPORT_ERROR


def decrypt_confidential_balance(
    balance_hex: str,
    privkey: str,
    range_low: int = 0,
    range_high: int = DEFAULT_DECRYPT_RANGE_HIGH,
) -> int:
    """Decrypt an on-ledger ElGamal balance blob to its plaintext amount.

    Convenience wrapper over :meth:`MPTCrypto.decrypt` that slices the 132-char
    hex ``c1 || c2`` blob for you. Use it to read your own confidential balance
    from an MPToken's ``ConfidentialBalanceSpending`` / ``ConfidentialBalanceInbox``
    (with the holder's private key), or the ``IssuerEncryptedBalance`` /
    ``AuditorEncryptedBalance`` mirror (with the issuer's / auditor's key).

    Decryption is a brute-force discrete-log search over
    ``[range_low, range_high]``; cost is O(range_high - range_low), so bound it
    as tightly as the issuance's outstanding amount allows.

    Args:
        balance_hex: 132-char hex ElGamal ciphertext (``c1 || c2``). An empty
            string (no confidential balance yet) returns 0.
        privkey: 64-char hex of the decrypting party's private key.
        range_low: Inclusive lower bound of the search range (default 0).
        range_high: Inclusive upper bound of the search range.

    Returns:
        The decrypted balance as a ``uint64``.

    Raises:
        ImportError: If the native mpt-crypto extension is not installed.
        ValueError: If ``balance_hex`` is non-empty but not 132 hex characters.
    """
    _require_native()
    if not balance_hex:
        return 0
    if len(balance_hex) != CIPHERTEXT_LENGTH:
        raise ValueError(
            f"balance_hex must be {CIPHERTEXT_LENGTH} hex characters "
            f"({CIPHERTEXT_LENGTH // 2}-byte c1||c2 ElGamal ciphertext)"
        )
    half = CIPHERTEXT_LENGTH // 2  # c1 is the first compressed point (66 hex)
    return crypto.decrypt(
        privkey, balance_hex[:half], balance_hex[half:], range_low, range_high
    )


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
    version = int(node.get("ConfidentialBalanceVersion", 0))
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


def _parse_mptoken_full(result: dict) -> Tuple[int, str, str]:
    node = result.get("node", {})
    return (
        int(node.get("ConfidentialBalanceVersion", 0)),
        node.get("ConfidentialBalanceSpending", ""),
        node.get("ConfidentialBalanceInbox", ""),
    )


def _mptoken_state_full(
    client: SyncClient, account: str, mpt_issuance_id: str
) -> Tuple[int, str, str]:
    resp = client.request(
        LedgerEntry(mptoken=MPToken(account=account, mpt_issuance_id=mpt_issuance_id))
    )
    return _parse_mptoken_full(resp.result)


async def _mptoken_state_full_async(
    client: AsyncClient, account: str, mpt_issuance_id: str
) -> Tuple[int, str, str]:
    resp = await client.request(
        LedgerEntry(mptoken=MPToken(account=account, mpt_issuance_id=mpt_issuance_id))
    )
    return _parse_mptoken_full(resp.result)


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
    _require_native()
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
    _require_native()
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


def predict_confidential_debit_state(
    version: int, balance_hex: str, encrypted_amount: str
) -> Tuple[int, str]:
    """
    Predict an account's ConfidentialBalanceSpending state after a debit applies.

    Mirrors rippled's ``chainAfterSend``: a confidential *debit* homomorphically
    decrements the spending balance by the transaction's encrypted amount
    (``new CB_S = CB_S - encryptedAmount``) and bumps the version by one. This is
    the same for a **ConfidentialMPTSend** (``sfSenderEncryptedAmount``) and a
    **ConfidentialMPTConvertBack** (``sfHolderEncryptedAmount``) — both spend from
    CB_S — so this primitive covers either.

    It is the debit primitive behind :func:`prepare_confidential_batch`. Use it
    directly only when composing a chain yourself (e.g. a multi-account Batch):
    each subsequent same-``(account, token)`` debit's proof must bind to the
    balance *after* the previous one applies, not the stale on-ledger value.

    Args:
        version: The ConfidentialBalanceVersion the previous debit bound to.
        balance_hex: The 132-char hex ConfidentialBalanceSpending (c1||c2) the
            previous debit bound to.
        encrypted_amount: The 132-char hex encrypted amount (c1||c2) of the
            previous debit (SenderEncryptedAmount or HolderEncryptedAmount).

    Returns:
        ``(next_version, next_balance_hex)`` for the following debit in the chain.
    """
    half = CIPHERTEXT_LENGTH // 2  # one compressed point = 66 hex chars
    new_c1, new_c2 = subtract_ciphertexts(
        balance_hex[:half],
        balance_hex[half:CIPHERTEXT_LENGTH],
        encrypted_amount[:half],
        encrypted_amount[half:CIPHERTEXT_LENGTH],
    )
    return version + 1, new_c1 + new_c2


def predict_confidential_merge_state(
    version: int, balance_hex: str, inbox_hex: str
) -> Tuple[int, str]:
    """
    Predict an account's ConfidentialBalanceSpending state after a MergeInbox.

    A ConfidentialMPTMergeInbox folds the inbox into the spending balance
    (``new CB_S = CB_S + inbox``; the inbox is then zeroed) and bumps the version
    by one — see rippled's ConfidentialMPTMergeInbox transactor. MergeInbox
    carries no proof of its own, but when it precedes a Send/ConvertBack in the
    same Batch that debit's proof must bind to this post-merge state.

    Args:
        version: The ConfidentialBalanceVersion before the merge.
        balance_hex: The 132-char hex ConfidentialBalanceSpending (c1||c2) before.
        inbox_hex: The 132-char hex ConfidentialBalanceInbox (c1||c2) being merged.

    Returns:
        ``(next_version, next_balance_hex)`` after the merge applies.
    """
    half = CIPHERTEXT_LENGTH // 2
    new_c1, new_c2 = add_ciphertexts(
        balance_hex[:half],
        balance_hex[half:CIPHERTEXT_LENGTH],
        inbox_hex[:half],
        inbox_hex[half:CIPHERTEXT_LENGTH],
    )
    return version + 1, new_c1 + new_c2


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
    _require_native()
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
    _require_native()
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


def _assemble_batch_chain(
    account: str,
    mpt_issuance_id: str,
    operations: List[ConfidentialBatchOp],
    first_inner_sequence: int,
    version: int,
    balance_hex: str,
    inbox_hex: str,
    range_high: int,
    account_privkey: str,
    account_pubkey: str,
    issuer_pubkey: str,
    auditor_pubkey: Optional[str],
) -> List[
    Union[ConfidentialMPTSend, ConfidentialMPTConvertBack, ConfidentialMPTMergeInbox]
]:
    """Thread predicted CB_S/version through an ordered chain of operations.

    Pure (client-free): the caller supplies the on-ledger starting state. Each
    op is assembled against the *current* predicted state, then that state is
    advanced to what rippled will leave after the op applies — a debit
    (Send/ConvertBack) subtracts its encrypted amount, a MergeInbox adds the
    inbox; every one bumps the version. Each inner is pinned to a consecutive
    sequence so batch autofill leaves them untouched (it only advances its
    counter for inners it assigns itself, which would otherwise collide).
    """
    _require_native()
    txs = []
    inbox_available = bool(inbox_hex)
    for i, op in enumerate(operations):
        sequence = first_inner_sequence + i
        if isinstance(op, ConfidentialSendOp):
            tx = _assemble_send(
                account,
                op.receiver_address,
                mpt_issuance_id,
                op.amount,
                sequence,
                version,
                balance_hex,
                range_high,
                account_privkey,
                account_pubkey,
                op.receiver_pubkey,
                issuer_pubkey,
                auditor_pubkey,
            )
            version, balance_hex = predict_confidential_debit_state(
                version, balance_hex, tx.sender_encrypted_amount
            )
        elif isinstance(op, ConfidentialConvertBackOp):
            tx = _assemble_convert_back(
                account,
                mpt_issuance_id,
                op.amount,
                sequence,
                version,
                balance_hex,
                range_high,
                account_privkey,
                account_pubkey,
                issuer_pubkey,
                auditor_pubkey,
            )
            version, balance_hex = predict_confidential_debit_state(
                version, balance_hex, tx.holder_encrypted_amount
            )
        elif isinstance(op, ConfidentialMergeInboxOp):
            # rippled's MergeInbox rejects (tecNO_PERMISSION) unless BOTH the
            # spending balance and a (non-consumed) inbox are present, so fail
            # fast here rather than build a Batch that will tec on-ledger. The
            # inbox is zeroed after the first merge, so a second merge in the
            # same chain has nothing left to fold in.
            if not balance_hex:
                raise ValueError(
                    "cannot merge inbox: account has no confidential spending "
                    "balance to merge into"
                )
            if not inbox_available:
                raise ValueError(
                    "cannot merge inbox: account has no inbox balance to merge "
                    "(a prior merge in this chain already consumed it)"
                )
            tx = ConfidentialMPTMergeInbox(
                account=account,
                mptoken_issuance_id=mpt_issuance_id,
                # Pin the sequence like the proof-bearing inners so autofill does
                # not reassign (and collide with) it, even though MergeInbox
                # itself carries no proof bound to the sequence.
                sequence=sequence,
            )
            version, balance_hex = predict_confidential_merge_state(
                version, balance_hex, inbox_hex
            )
            inbox_available = False  # inbox is zeroed on-ledger by this merge
        else:
            raise TypeError(
                f"unsupported confidential batch operation: {type(op).__name__}"
            )
        txs.append(tx)
    return txs


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


def prepare_confidential_batch(
    client: SyncClient,
    wallet: Wallet,
    mpt_issuance_id: str,
    operations: List[ConfidentialBatchOp],
    account_privkey: str,
    account_pubkey: str,
    issuer_pubkey: str,
    auditor_pubkey: Optional[str] = None,
    first_inner_sequence: Optional[int] = None,
) -> List[
    Union[ConfidentialMPTSend, ConfidentialMPTConvertBack, ConfidentialMPTMergeInbox]
]:
    """
    Prepare a chain of confidential inner transactions for one Batch.

    Every confidential transaction that touches an account's spending balance
    mutates it: a **Send** and a **ConvertBack** each debit it
    (``CB_S = CB_S - encryptedAmount``) and a **MergeInbox** credits it from the
    inbox (``CB_S = CB_S + inbox``) — and all three bump the ConfidentialBalance-
    Version. So when a single Batch contains several such operations for the
    *same* ``(account, token)``, each proof-bearing one (Send/ConvertBack) must
    bind to the balance/version left by the operations before it, not the stale
    on-ledger value. This builder queries the on-ledger state once, then threads
    the predicted CB_S/version through ``operations`` in order (via
    :func:`predict_confidential_debit_state` /
    :func:`predict_confidential_merge_state`), pinning each inner to a
    consecutive sequence number.

    Provide operations as :class:`ConfidentialSendOp`,
    :class:`ConfidentialConvertBackOp`, and :class:`ConfidentialMergeInboxOp`.
    Convert and Clawback never prove against this account's CB_S/version, so they
    are not chained here — add them to the ``Batch`` as plain inner transactions
    (a same-account Convert credits the inbox, so do not place one before a
    MergeInbox in this chain, whose inbox is predicted from the on-ledger value).

    The returned transactions drop into a ``Batch``'s ``raw_transactions`` in
    order. Inner-Batch sequencing gives the outer Batch account its current
    sequence ``S`` then ``S+1, S+2, ...`` to its inners, so the first inner is
    pinned to ``S+1`` by default. Pass ``first_inner_sequence`` for any other
    arrangement (multi-account Batch where this account is not the outer account,
    or a ticket-based Batch).

    Two sequencing caveats:

    * These inners are pinned, so ``autofill`` will not renumber them. If you
      also append your *own* same-account inners (a plain Convert/Clawback, or a
      non-confidential Payment), pin each to
      ``first_inner_sequence + len(operations) + i`` — batch autofill only
      advances its counter for inners it assigns itself, so an unpinned extra
      inner would be given ``first_inner_sequence`` again and collide.
    * The pinned sequences assume no other transaction from this account is
      submitted between building and submitting the Batch. If one is (shifting
      ``S``), rebuild — the proofs are bound to these exact sequence values and
      cannot be renumbered.

    Args:
        client: XRPL client (used to query sequence, balance, version, inbox).
        wallet: Wallet of the account whose confidential balance is spent/merged.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string). All operations are
            for this same issuance — chaining is per ``(account, token)``.
        operations: Ordered list of confidential batch operations.
        account_privkey: 64-char hex of the account's confidential private key.
        account_pubkey: 66-char hex of the account's compressed public key.
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        auditor_pubkey: Optional 66-char hex of the auditor's public key.
        first_inner_sequence: Sequence to pin the first inner to. Defaults to the
            account's next sequence + 1 (the account-batches-own-ops case).

    Returns:
        The inner transactions, correctly chained and sequence-pinned, in the
        same order as ``operations``.

    Raises:
        ValueError: If ``operations`` is empty.
        TypeError: If an entry is not a recognized confidential batch operation.
    """
    _require_native()
    if not operations:
        raise ValueError("operations must contain at least one confidential operation")

    version, balance_hex, inbox_hex = _mptoken_state_full(
        client, wallet.classic_address, mpt_issuance_id
    )
    range_high = _decrypt_range_high(client, mpt_issuance_id)
    if first_inner_sequence is None:
        first_inner_sequence = _account_sequence(client, wallet.address) + 1

    return _assemble_batch_chain(
        wallet.address,
        mpt_issuance_id,
        operations,
        first_inner_sequence,
        version,
        balance_hex,
        inbox_hex,
        range_high,
        account_privkey,
        account_pubkey,
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


async def prepare_confidential_batch_async(
    client: AsyncClient,
    wallet: Wallet,
    mpt_issuance_id: str,
    operations: List[ConfidentialBatchOp],
    account_privkey: str,
    account_pubkey: str,
    issuer_pubkey: str,
    auditor_pubkey: Optional[str] = None,
    first_inner_sequence: Optional[int] = None,
) -> List[
    Union[ConfidentialMPTSend, ConfidentialMPTConvertBack, ConfidentialMPTMergeInbox]
]:
    """
    Async variant of :func:`prepare_confidential_batch`.

    Args:
        client: Async XRPL client.
        wallet: Wallet of the account whose confidential balance is spent/merged.
        mpt_issuance_id: 24-byte MPT issuance ID (hex string). All operations are
            for this same issuance — chaining is per ``(account, token)``.
        operations: Ordered list of confidential batch operations.
        account_privkey: 64-char hex of the account's confidential private key.
        account_pubkey: 66-char hex of the account's compressed public key.
        issuer_pubkey: 66-char hex of the issuer's compressed public key.
        auditor_pubkey: Optional 66-char hex of the auditor's public key.
        first_inner_sequence: Sequence to pin the first inner to. Defaults to the
            account's next sequence + 1.

    Returns:
        The inner transactions, correctly chained and sequence-pinned, in the
        same order as ``operations``.

    Raises:
        ValueError: If ``operations`` is empty.
        TypeError: If an entry is not a recognized confidential batch operation.
    """
    _require_native()
    if not operations:
        raise ValueError("operations must contain at least one confidential operation")

    version, balance_hex, inbox_hex = await _mptoken_state_full_async(
        client, wallet.classic_address, mpt_issuance_id
    )
    range_high = await _decrypt_range_high_async(client, mpt_issuance_id)
    if first_inner_sequence is None:
        first_inner_sequence = await _account_sequence_async(client, wallet.address) + 1

    return _assemble_batch_chain(
        wallet.address,
        mpt_issuance_id,
        operations,
        first_inner_sequence,
        version,
        balance_hex,
        inbox_hex,
        range_high,
        account_privkey,
        account_pubkey,
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
