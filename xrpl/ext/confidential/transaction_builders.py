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
# confidential inner transaction and carries its own account, token, and keys, so
# a single Batch can mix operations across MULTIPLE accounts and MULTIPLE tokens.
# The builder threads a predicted confidential state per ``(account, token)``
# MPToken through the ops in order: every proof-bearing inner (Send/ConvertBack/
# Clawback) binds to the balance/version the prior inners leave behind. All five
# confidential transaction types are supported:
#   - Convert     credits the holder's inbox + mirrors (no version bump).
#   - Send        debits the sender's balances (+version) AND credits the
#                 destination's inbox + mirrors.
#   - ConvertBack debits the account's balances (+version).
#   - MergeInbox  folds the inbox into spending, zeroes the inbox (+version).
#   - Clawback    resets the holder's balances to encrypted-zero (+version).
# Mirrors xrpl.js's prepareConfidentialBatch. (The Rust sister supports only the
# narrower single-account Send/ConvertBack/MergeInbox chain.)
# ──────────────────────────────────────────────────────────────────────────────
_PUBKEY_HEX_LEN = 66  # 33-byte compressed secp256k1 public key


@dataclass(frozen=True)
class ConfidentialConvertOp:
    """Convert ``amount`` of ``account``'s public balance into confidential form.

    On a holder's first convert this also registers ``holder_pubkey`` (the
    builder detects registration from predicted state, so two converts of the
    same new holder in one Batch register the key only once).
    """

    account: str
    mpt_issuance_id: str
    amount: int
    holder_privkey: str
    holder_pubkey: str
    issuer_pubkey: str
    auditor_pubkey: Optional[str] = None

    def __post_init__(self: Self) -> None:
        """Validate the fields (called by dataclasses after __init__)."""
        # A zero amount is valid for Convert (the key-registration path).
        if self.amount < 0:
            raise ValueError("amount cannot be negative")
        _check_pubkey(self.holder_pubkey, "holder_pubkey")


@dataclass(frozen=True)
class ConfidentialSendOp:
    """A confidential transfer of ``amount`` from ``account`` to a receiver."""

    account: str
    mpt_issuance_id: str
    receiver_address: str
    receiver_pubkey: str
    amount: int
    sender_privkey: str
    sender_pubkey: str
    issuer_pubkey: str
    auditor_pubkey: Optional[str] = None

    def __post_init__(self: Self) -> None:
        """Validate the fields (called by dataclasses after __init__)."""
        # receiver_address and receiver_pubkey are both str and adjacent; a swap
        # would otherwise build a valid-looking op whose proof binds the wrong
        # key and only fails on-ledger. The pubkey is a 66-char hex compressed
        # key; an XRPL address never is, so this catches the swap early.
        _check_pubkey(
            self.receiver_pubkey,
            "receiver_pubkey",
            "(did you swap receiver_address and receiver_pubkey?)",
        )
        if self.amount <= 0:
            raise ValueError("amount must be a positive integer")


@dataclass(frozen=True)
class ConfidentialConvertBackOp:
    """Convert ``amount`` of ``account``'s confidential balance back to public."""

    account: str
    mpt_issuance_id: str
    amount: int
    holder_privkey: str
    holder_pubkey: str
    issuer_pubkey: str
    auditor_pubkey: Optional[str] = None

    def __post_init__(self: Self) -> None:
        """Validate the fields (called by dataclasses after __init__)."""
        if self.amount <= 0:
            raise ValueError("amount must be a positive integer")


@dataclass(frozen=True)
class ConfidentialMergeInboxOp:
    """Merge ``account``'s inbox balance into its spending balance."""

    account: str
    mpt_issuance_id: str


@dataclass(frozen=True)
class ConfidentialClawbackOp:
    """Issuer ``account`` claws back ``holder``'s entire confidential balance."""

    account: str
    mpt_issuance_id: str
    holder: str
    amount: int
    issuer_privkey: str
    issuer_pubkey: str
    auditor_pubkey: Optional[str] = None

    def __post_init__(self: Self) -> None:
        """Validate the fields (called by dataclasses after __init__)."""
        if self.amount <= 0:
            raise ValueError("amount must be a positive integer")


ConfidentialBatchOp = Union[
    ConfidentialConvertOp,
    ConfidentialSendOp,
    ConfidentialConvertBackOp,
    ConfidentialMergeInboxOp,
    ConfidentialClawbackOp,
]


def _check_pubkey(value: str, field: str, hint: str = "") -> None:
    if len(value) != _PUBKEY_HEX_LEN:
        suffix = f" {hint}" if hint else ""
        raise ValueError(
            f"{field} must be a {_PUBKEY_HEX_LEN}-char hex compressed "
            f"public key{suffix}"
        )


def _op_account(op: ConfidentialBatchOp) -> str:
    """The account whose sequence an op consumes (its submitter)."""
    return op.account


def _op_state_key(op: ConfidentialBatchOp) -> Tuple[str, str]:
    """The ``(holder, token)`` MPToken an op's own proof/state reads or mutates.

    For a Clawback this is the *holder's* MPToken (the issuer holds none); for
    every other op it is the submitting account's own MPToken.
    """
    if isinstance(op, ConfidentialClawbackOp):
        return (op.holder, op.mpt_issuance_id)
    return (op.account, op.mpt_issuance_id)


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


@dataclass
class _TokenState:
    """Predicted confidential state of one ``(account, token)`` MPToken.

    Threaded through the batch as it is built. A ``None`` balance is one a prior
    inner reset to the canonical encrypted zero (MergeInbox clears the inbox;
    Clawback clears everything) — the client cannot reproduce it, so a later
    inner that needs it raises rather than emit a proof rippled would reject.
    """

    spending: Optional[str] = None
    inbox: Optional[str] = None
    issuer_enc: Optional[str] = None
    auditor_enc: Optional[str] = None
    version: int = 0
    holder_key: Optional[str] = None


def _parse_token_state(result: dict) -> _TokenState:
    node = result.get("node", {})

    def field(name: str) -> Optional[str]:
        # rippled returns absent confidential fields as missing keys or "".
        value = node.get(name)
        return value if value else None

    return _TokenState(
        spending=field("ConfidentialBalanceSpending"),
        inbox=field("ConfidentialBalanceInbox"),
        issuer_enc=field("IssuerEncryptedBalance"),
        auditor_enc=field("AuditorEncryptedBalance"),
        version=int(node.get("ConfidentialBalanceVersion", 0)),
        holder_key=field("HolderEncryptionKey"),
    )


def _fetch_token_state(
    client: SyncClient, account: str, mpt_issuance_id: str
) -> _TokenState:
    resp = client.request(
        LedgerEntry(mptoken=MPToken(account=account, mpt_issuance_id=mpt_issuance_id))
    )
    return _parse_token_state(resp.result)


async def _fetch_token_state_async(
    client: AsyncClient, account: str, mpt_issuance_id: str
) -> _TokenState:
    resp = await client.request(
        LedgerEntry(mptoken=MPToken(account=account, mpt_issuance_id=mpt_issuance_id))
    )
    return _parse_token_state(resp.result)


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


# ──────────────────────────────────────────────────────────────────────────────
# Multi-account / multi-token batch state machine. Each op is assembled against
# the current predicted state of the (account, token) MPToken(s) it touches, then
# that state is advanced to what rippled leaves after the op applies. Mirrors
# xrpl.js's prepareConfidentialBatch state transitions.
# ──────────────────────────────────────────────────────────────────────────────
_HALF = CIPHERTEXT_LENGTH // 2  # one compressed ElGamal point = 66 hex chars
# A confidential proof binds the first 32 bytes (64 hex) of its ZKProof as the
# re-randomization challenge; rippled reuses it to re-blind a Send destination's
# credited balances, so we reproduce that to predict the recipient's post-send
# state.
_CHALLENGE_HEX_LEN = 64
# rippled caps a Batch at kMaxBatchTxCount = 8 inner transactions (STTx.cpp).
_MAX_BATCH_INNERS = 8


def _add(a: str, b: str) -> str:
    c1, c2 = add_ciphertexts(a[:_HALF], a[_HALF:], b[:_HALF], b[_HALF:])
    return c1 + c2


def _sub(a: str, b: str) -> str:
    c1, c2 = subtract_ciphertexts(a[:_HALF], a[_HALF:], b[:_HALF], b[_HALF:])
    return c1 + c2


def _read_balance(value: Optional[str], what: str) -> str:
    if not value:
        raise ValueError(
            f"cannot predict {what}: an earlier MergeInbox or Clawback in this "
            "Batch reset it to a value the client cannot reproduce. Split these "
            "operations across separate Batches."
        )
    return value


def _reblind(ciphertext: str, pubkey: str, challenge: str) -> str:
    # rippled re-randomizes a credited ciphertext by homomorphically adding
    # enc(0, key, challenge) — a deterministic zero-encryption under the proof
    # challenge. Reproduce it so the predicted balance matches the ledger.
    zero_c1, zero_c2, _ = crypto.encrypt(pubkey, 0, challenge)
    return _add(ciphertext, zero_c1 + zero_c2)


def _apply_debit(
    state: _TokenState,
    spend: str,
    issuer: str,
    auditor: Optional[str],
) -> _TokenState:
    # Send sender / ConvertBack: subtract the encrypted amount from spending,
    # issuer-encrypted, and (if present) auditor-encrypted balances; bump version.
    return _TokenState(
        spending=_sub(_read_balance(state.spending, "spending balance"), spend),
        inbox=state.inbox,
        issuer_enc=_sub(
            _read_balance(state.issuer_enc, "issuer-encrypted balance"), issuer
        ),
        auditor_enc=(
            state.auditor_enc
            if auditor is None
            else _sub(
                _read_balance(state.auditor_enc, "auditor-encrypted balance"), auditor
            )
        ),
        version=state.version + 1,
        holder_key=state.holder_key,
    )


def _apply_convert_credit(
    state: _TokenState,
    inbox: str,
    issuer: str,
    auditor: Optional[str],
) -> _TokenState:
    # Convert credits the holder's pending inbox + mirror balances (a first-ever
    # convert initializes an absent balance to the encrypted amount). Spending is
    # untouched and the version does NOT bump.
    auditor_enc = state.auditor_enc
    if auditor is not None:
        auditor_enc = auditor if auditor_enc is None else _add(auditor_enc, auditor)
    return _TokenState(
        spending=state.spending,
        inbox=inbox if state.inbox is None else _add(state.inbox, inbox),
        issuer_enc=(
            issuer if state.issuer_enc is None else _add(state.issuer_enc, issuer)
        ),
        auditor_enc=auditor_enc,
        version=state.version,
        holder_key=state.holder_key,
    )


def _apply_merge(state: _TokenState) -> _TokenState:
    spending = _add(
        _read_balance(state.spending, "spending balance"),
        _read_balance(state.inbox, "inbox balance"),
    )
    # rippled resets the inbox to the canonical encrypted zero (uncomputable here).
    return _TokenState(
        spending=spending,
        inbox=None,
        issuer_enc=state.issuer_enc,
        auditor_enc=state.auditor_enc,
        version=state.version + 1,
        holder_key=state.holder_key,
    )


def _apply_clawback(state: _TokenState) -> _TokenState:
    # A clawback burns the holder's entire confidential holding: all balances
    # reset to the canonical encrypted zero, version bumps.
    return _TokenState(version=state.version + 1, holder_key=state.holder_key)


def _apply_inbox_credit(
    dest: _TokenState,
    tx: ConfidentialMPTSend,
    issuer_pubkey: str,
    auditor_pubkey: Optional[str],
) -> _TokenState:
    # rippled credits the destination's inbox AND its issuer/auditor mirror
    # balances on a Send, each re-blinded with the proof challenge. (xrpl.js only
    # advances the inbox, which mispredicts a same-batch Clawback of the recipient;
    # we advance all three so that case chains correctly.)
    challenge = tx.zk_proof[:_CHALLENGE_HEX_LEN]
    dest_key = _read_balance(dest.holder_key, "destination holder key")
    inbox = _add(
        _read_balance(dest.inbox, "destination inbox balance"),
        _reblind(tx.destination_encrypted_amount, dest_key, challenge),
    )
    issuer_enc = _add(
        _read_balance(dest.issuer_enc, "destination issuer-encrypted balance"),
        _reblind(tx.issuer_encrypted_amount, issuer_pubkey, challenge),
    )
    auditor_enc = dest.auditor_enc
    if tx.auditor_encrypted_amount is not None and auditor_pubkey is not None:
        auditor_enc = _add(
            _read_balance(dest.auditor_enc, "destination auditor-encrypted balance"),
            _reblind(tx.auditor_encrypted_amount, auditor_pubkey, challenge),
        )
    return _TokenState(
        spending=dest.spending,
        inbox=inbox,
        issuer_enc=issuer_enc,
        auditor_enc=auditor_enc,
        version=dest.version,
        holder_key=dest.holder_key,
    )


def _sum_converts_by_token(operations: List[ConfidentialBatchOp]) -> dict:
    # The most a token's ConfidentialOutstandingAmount can rise within the batch;
    # threaded into each spend's decrypt bound so a balance topped up by an
    # in-batch Convert stays decryptable against the pre-batch total.
    totals: dict = {}
    for op in operations:
        if isinstance(op, ConfidentialConvertOp):
            totals[op.mpt_issuance_id] = totals.get(op.mpt_issuance_id, 0) + op.amount
    return totals


def _build_confidential_inner(
    op: ConfidentialBatchOp,
    sequence: int,
    states: dict,
    range_high: int,
) -> Tuple[object, List[Tuple[Tuple[str, str], _TokenState]]]:
    """Build one inner against the current predicted state and return the state
    updates it implies (applied by the caller so this stays pure w.r.t. the map).
    """
    key = _op_state_key(op)
    state = states.get(key, _TokenState())

    if isinstance(op, ConfidentialConvertOp):
        tx = _assemble_convert(
            op.account,
            op.mpt_issuance_id,
            op.amount,
            sequence,
            op.issuer_pubkey,
            op.holder_privkey,
            op.holder_pubkey,
            op.auditor_pubkey,
            state.holder_key is not None,
        )
        credited = _apply_convert_credit(
            state,
            tx.holder_encrypted_amount,
            tx.issuer_encrypted_amount,
            tx.auditor_encrypted_amount,
        )
        # A Convert publishes the holder's ElGamal key; record it so a later
        # same-batch Send to this holder encrypts to it before it is on-ledger.
        credited.holder_key = op.holder_pubkey
        return tx, [(key, credited)]

    if isinstance(op, ConfidentialSendOp):
        dest_key = (op.receiver_address, op.mpt_issuance_id)
        dest = states.get(dest_key, _TokenState())
        tx = _assemble_send(
            op.account,
            op.receiver_address,
            op.mpt_issuance_id,
            op.amount,
            sequence,
            state.version,
            _read_balance(state.spending, f"{op.account} spending balance"),
            range_high,
            op.sender_privkey,
            op.sender_pubkey,
            op.receiver_pubkey,
            op.issuer_pubkey,
            op.auditor_pubkey,
        )
        debited = _apply_debit(
            state,
            tx.sender_encrypted_amount,
            tx.issuer_encrypted_amount,
            tx.auditor_encrypted_amount,
        )
        credited = _apply_inbox_credit(dest, tx, op.issuer_pubkey, op.auditor_pubkey)
        return tx, [(key, debited), (dest_key, credited)]

    if isinstance(op, ConfidentialConvertBackOp):
        tx = _assemble_convert_back(
            op.account,
            op.mpt_issuance_id,
            op.amount,
            sequence,
            state.version,
            _read_balance(state.spending, f"{op.account} spending balance"),
            range_high,
            op.holder_privkey,
            op.holder_pubkey,
            op.issuer_pubkey,
            op.auditor_pubkey,
        )
        debited = _apply_debit(
            state,
            tx.holder_encrypted_amount,
            tx.issuer_encrypted_amount,
            tx.auditor_encrypted_amount,
        )
        return tx, [(key, debited)]

    if isinstance(op, ConfidentialMergeInboxOp):
        # rippled's MergeInbox rejects unless BOTH the spending balance and a
        # (non-consumed) inbox are present; fail fast rather than tec on-ledger.
        if state.spending is None:
            raise ValueError(
                "cannot merge inbox: account has no confidential spending balance "
                "to merge into"
            )
        if state.inbox is None:
            raise ValueError(
                "cannot merge inbox: account has no inbox balance to merge (a "
                "prior merge or clawback in this chain already consumed it)"
            )
        tx = ConfidentialMPTMergeInbox(
            account=op.account,
            mptoken_issuance_id=op.mpt_issuance_id,
            # Pin the sequence like the proof-bearing inners so autofill does not
            # reassign it, even though MergeInbox carries no proof.
            sequence=sequence,
        )
        return tx, [(key, _apply_merge(state))]

    if isinstance(op, ConfidentialClawbackOp):
        tx = _assemble_clawback(
            op.account,
            op.holder,
            op.mpt_issuance_id,
            op.amount,
            sequence,
            op.issuer_privkey,
            op.issuer_pubkey,
            _read_balance(state.issuer_enc, f"{op.holder} issuer-encrypted balance"),
        )
        return tx, [(key, _apply_clawback(state))]

    raise TypeError(f"unsupported confidential batch operation: {type(op).__name__}")


def _assemble_multi_account_batch(
    operations: List[ConfidentialBatchOp],
    states: dict,
    next_sequence: dict,
    range_highs: dict,
) -> List[object]:
    """Thread predicted per-(account, token) state through the ordered ops.

    Pure (client-free): the caller supplies the fetched starting ``states``, the
    per-account ``next_sequence`` counters, and per-token ``range_highs``. Each op
    consumes its account's next sequence and is assembled against the current
    predicted state, which is then advanced.
    """
    _require_native()
    txs: List[object] = []
    for op in operations:
        account = _op_account(op)
        sequence = next_sequence[account]
        next_sequence[account] = sequence + 1
        tx, updates = _build_confidential_inner(
            op, sequence, states, range_highs[op.mpt_issuance_id]
        )
        for state_key, new_state in updates:
            states[state_key] = new_state
        txs.append(tx)
    return txs


def _validate_batch_size(operations: List[ConfidentialBatchOp]) -> None:
    # rippled bounds a Batch to 2-8 inners, but a caller may compose these
    # confidential ops with additional plain inners (e.g. an XRP Payment) to reach
    # the minimum, so only the upper bound is enforceable from the ops alone.
    if not operations:
        raise ValueError("operations must contain at least one confidential operation")
    if len(operations) > _MAX_BATCH_INNERS:
        raise ValueError(
            f"a Batch allows at most {_MAX_BATCH_INNERS} inner transactions, "
            f"got {len(operations)}"
        )


def _batch_state_keys(operations: List[ConfidentialBatchOp]) -> set:
    # Every (account, token) MPToken the batch reads or mutates: each op's own
    # state key, plus a send's destination.
    keys = set()
    for op in operations:
        keys.add(_op_state_key(op))
        if isinstance(op, ConfidentialSendOp):
            keys.add((op.receiver_address, op.mpt_issuance_id))
    return keys


def _next_sequences(current: dict, batch_account: str) -> dict:
    # Mirror autofillBatchTxn: the outer Batch account's inners start at its
    # current sequence + 1 (the outer Batch consumes the current one); every
    # other account's inners start at its own current sequence.
    return {
        account: (seq + 1 if account == batch_account else seq)
        for account, seq in current.items()
    }


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
    batch_account: str,
    operations: List[ConfidentialBatchOp],
) -> List[object]:
    """
    Assemble the confidential inner transactions for one XLS-56 Batch.

    A single Batch may mix any of the five confidential operations across
    **multiple accounts** and **multiple tokens**. Each op carries its own
    account, ``mpt_issuance_id``, and keys (see :class:`ConfidentialConvertOp`,
    :class:`ConfidentialSendOp`, :class:`ConfidentialConvertBackOp`,
    :class:`ConfidentialMergeInboxOp`, :class:`ConfidentialClawbackOp`).

    The subtlety this builder owns: a confidential proof binds the balance and
    version of the ``(account, token)`` MPToken it spends, so when several inners
    touch the same MPToken each must bind to the state the previous ones leave
    behind, not the stale on-ledger value. The builder fetches every referenced
    MPToken's state once (each op's own, plus a send's destination), then threads
    the predicted state — spending, inbox, issuer/auditor mirrors, version, and
    holder key — through the ops in order:

    * **Convert** credits the holder's inbox + mirrors (no version bump) and
      registers the holder key (only the first convert of a new holder does).
    * **Send** debits the sender's balances (+version) and credits the
      destination's inbox + mirrors.
    * **ConvertBack** debits the account's balances (+version).
    * **MergeInbox** folds the inbox into spending and zeroes the inbox
      (+version).
    * **Clawback** resets the holder's balances (+version).

    Each inner is pinned to a per-account consecutive sequence, mirroring how
    ``autofill`` sequences a Batch: the outer Batch account's inners start at its
    current sequence + 1 (the outer Batch consumes the current one); every other
    account's inners start at its own current sequence. A confidential proof binds
    its sequence, so autofill must not renumber it.

    The returned transactions drop into a ``Batch``'s ``raw_transactions`` in
    order; ``batch_account`` is the account that submits (and signs) the outer
    Batch. Signing stays with the caller: ``sign_multi_batch`` for each non-outer
    participant, then the outer account signs. A balance a prior MergeInbox or
    Clawback reset to encrypted-zero cannot be predicted; an inner that reads one
    raises — split those across separate Batches.

    Args:
        client: XRPL client (used to query per-account sequence and per-MPToken
            confidential state).
        batch_account: Classic address of the account submitting the outer Batch.
        operations: Ordered list of confidential batch operations (1-8; may be
            composed with plain inners to reach the Batch minimum of 2).

    Returns:
        The inner transactions, correctly chained and sequence-pinned, in the
        same order as ``operations``.

    Raises:
        ValueError: If ``operations`` is empty or exceeds 8 entries, or a chain
            reads a balance a prior MergeInbox/Clawback reset.
        TypeError: If an entry is not a recognized confidential batch operation.
    """
    _require_native()
    _validate_batch_size(operations)

    states = {
        key: _fetch_token_state(client, key[0], key[1])
        for key in _batch_state_keys(operations)
    }
    convert_totals = _sum_converts_by_token(operations)
    range_highs = {
        token: _decrypt_range_high(client, token) + convert_totals.get(token, 0)
        for token in {op.mpt_issuance_id for op in operations}
    }
    accounts = {batch_account} | {_op_account(op) for op in operations}
    current = {account: _account_sequence(client, account) for account in accounts}

    return _assemble_multi_account_batch(
        operations, states, _next_sequences(current, batch_account), range_highs
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
    batch_account: str,
    operations: List[ConfidentialBatchOp],
) -> List[object]:
    """
    Async variant of :func:`prepare_confidential_batch`.

    Args:
        client: Async XRPL client.
        batch_account: Classic address of the account submitting the outer Batch.
        operations: Ordered list of confidential batch operations (1-8; may be
            composed with plain inners to reach the Batch minimum of 2).

    Returns:
        The inner transactions, correctly chained and sequence-pinned, in the
        same order as ``operations``.

    Raises:
        ValueError: If ``operations`` is empty or exceeds 8 entries, or a chain
            reads a balance a prior MergeInbox/Clawback reset.
        TypeError: If an entry is not a recognized confidential batch operation.
    """
    _require_native()
    _validate_batch_size(operations)

    states = {
        key: await _fetch_token_state_async(client, key[0], key[1])
        for key in _batch_state_keys(operations)
    }
    convert_totals = _sum_converts_by_token(operations)
    range_highs = {
        token: await _decrypt_range_high_async(client, token)
        + convert_totals.get(token, 0)
        for token in {op.mpt_issuance_id for op in operations}
    }
    accounts = {batch_account} | {_op_account(op) for op in operations}
    current = {
        account: await _account_sequence_async(client, account) for account in accounts
    }

    return _assemble_multi_account_batch(
        operations, states, _next_sequences(current, batch_account), range_highs
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
