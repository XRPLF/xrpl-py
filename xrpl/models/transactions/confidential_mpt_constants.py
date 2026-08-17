"""Canonical sizes for Confidential MPT (XLS-0096) fields and zero-knowledge proofs.

Single source of truth for the model-layer length validations shared by the
``ConfidentialMPT*`` transactions. The byte sizes mirror the mpt-crypto library
constants (``SECP256K1_*_PROOF_SIZE`` / ``kMPT_*``); the native integration test
``tests/unit/core/confidential/test_utility_layer`` cross-checks them against the
compiled library so the two cannot silently drift across a version bump.

This module is pure-Python and importable without the native extension.
"""

from typing import Final, Optional

from xrpl.core.addresscodec import decode_classic_address
from xrpl.core.addresscodec.exceptions import XRPLAddressCodecException
from xrpl.models.utils import HEX_REGEX

# Maximum representable MPT amount: 2**63 - 1 (maxMPTokenAmount). MPT amounts
# serialize as an unsigned 64-bit integer but are capped at i64::MAX on-ledger,
# matching rippled's maxMPTokenAmount and the JS/Rust SDKs' MAX_MPT_AMOUNT.
MAX_MPT_AMOUNT: Final[int] = 2**63 - 1

# Hex-character offsets of the issuer's AccountID within an MPTokenIssuanceID.
# The 24-byte ID is sequence(4) || issuerAccountID(20), so the 20-byte issuer
# occupies hex characters [8, 48) (mirrors rippled MPTIssue::getIssuer, which
# skips the 4-byte sequence prefix).
_ISSUER_HEX_START: Final[int] = 8
_ISSUER_HEX_END: Final[int] = 48

# --- Primitive byte sizes (mirror mpt_protocol.h) ---
SCHNORR_PROOF_SIZE: Final[int] = 64
ELGAMAL_TOTAL_SIZE: Final[int] = 66
PEDERSEN_COMMIT_SIZE: Final[int] = 33
BLINDING_FACTOR_SIZE: Final[int] = 32
PUBKEY_COMPRESSED_SIZE: Final[int] = 33

# --- Compact sigma + bulletproof component byte sizes ---
COMPACT_CLAWBACK_PROOF_SIZE: Final[int] = 64
COMPACT_CONVERTBACK_PROOF_SIZE: Final[int] = 128
COMPACT_STANDARD_PROOF_SIZE: Final[int] = 192
SINGLE_BULLETPROOF_SIZE: Final[int] = 688
DOUBLE_BULLETPROOF_SIZE: Final[int] = 754

# --- Composite ZKProof byte sizes (what the ZKProof field carries) ---
CLAWBACK_PROOF_SIZE: Final[int] = COMPACT_CLAWBACK_PROOF_SIZE  # 64
CONVERT_BACK_PROOF_SIZE: Final[int] = (
    COMPACT_CONVERTBACK_PROOF_SIZE + SINGLE_BULLETPROOF_SIZE
)  # 816
SEND_PROOF_SIZE: Final[int] = (
    COMPACT_STANDARD_PROOF_SIZE + DOUBLE_BULLETPROOF_SIZE
)  # 946

# --- Hex-character lengths used by model validation (2 hex chars per byte) ---
HOLDER_ENCRYPTION_KEY_LENGTH: Final[int] = PUBKEY_COMPRESSED_SIZE * 2  # 66
BLINDING_FACTOR_LENGTH: Final[int] = BLINDING_FACTOR_SIZE * 2  # 64
SCHNORR_PROOF_LENGTH: Final[int] = SCHNORR_PROOF_SIZE * 2  # 128
CIPHERTEXT_LENGTH: Final[int] = ELGAMAL_TOTAL_SIZE * 2  # 132
COMMITMENT_LENGTH: Final[int] = PEDERSEN_COMMIT_SIZE * 2  # 66
CLAWBACK_PROOF_LENGTH: Final[int] = CLAWBACK_PROOF_SIZE * 2  # 128
SEND_PROOF_LENGTH: Final[int] = SEND_PROOF_SIZE * 2  # 1892
CONVERT_BACK_PROOF_LENGTH: Final[int] = CONVERT_BACK_PROOF_SIZE * 2  # 1632

# MPTokenIssuanceID is 24 bytes (4-byte Sequence + 20-byte issuer AccountID),
# i.e. 48 hex characters — shared by every ConfidentialMPT* transaction.
MPT_ISSUANCE_ID_LENGTH: Final[int] = 48


def get_mptoken_issuance_id_error(mptoken_issuance_id: str) -> Optional[str]:
    """Validate a hex-encoded ``MPTokenIssuanceID``.

    Returns an error message if ``mptoken_issuance_id`` is not exactly
    ``MPT_ISSUANCE_ID_LENGTH`` (48) hex characters, otherwise ``None``. Shared by
    the ``ConfidentialMPT*`` models; mirrors xrpl-rust's
    ``validate_mptoken_issuance_id``.

    Args:
        mptoken_issuance_id: The candidate MPTokenIssuanceID hex string.

    Returns:
        An error string, or ``None`` if the value is a valid MPTokenIssuanceID.
    """
    if len(mptoken_issuance_id) != MPT_ISSUANCE_ID_LENGTH or not HEX_REGEX.fullmatch(
        mptoken_issuance_id
    ):
        return (
            f"mptoken_issuance_id must be a {MPT_ISSUANCE_ID_LENGTH}-character hex "
            "string (24-byte MPTokenIssuanceID)"
        )
    return None


def get_mpt_amount_error(mpt_amount: int, *, allow_zero: bool) -> Optional[str]:
    """Validate a plaintext ``MPTAmount``: sign and the on-ledger upper bound.

    Mirrors rippled's ``temBAD_AMOUNT`` preflight and xrpl-rust's
    ``validate_mpt_amount``. ``ConfidentialMPTConvert`` permits a zero amount (the
    key-registration path); ``ConfidentialMPTConvertBack`` and
    ``ConfidentialMPTClawback`` require a positive amount.

    Args:
        mpt_amount: The candidate amount.
        allow_zero: Whether zero is a valid amount.

    Returns:
        An error string, or ``None`` if the value is a valid MPTAmount.
    """
    if allow_zero:
        if mpt_amount < 0:
            return "mpt_amount cannot be negative"
    elif mpt_amount <= 0:
        return "mpt_amount cannot be zero or negative"
    if mpt_amount > MAX_MPT_AMOUNT:
        return (
            f"mpt_amount must not exceed {MAX_MPT_AMOUNT} (maxMPTokenAmount, 2**63 - 1)"
        )
    return None


def address_is_issuer(mptoken_issuance_id: str, address: str) -> bool:
    """Return whether ``address`` is the issuer encoded in ``mptoken_issuance_id``.

    Used to enforce rippled's ``temMALFORMED`` issuer-role preflight bans (e.g. the
    issuer cannot be the sender/destination of a ``ConfidentialMPTSend`` and must be
    the account of a ``ConfidentialMPTClawback``). Mirrors rippled
    ``MPTIssue::getIssuer`` and xrpl-rust's ``address_is_issuer``: the issuer is the
    20-byte AccountID at hex chars ``[8, 48)`` of the issuance ID.

    A malformed address or too-short issuance ID yields ``False`` — the dedicated
    format checks surface those — so this only reports a positive issuer match.

    Args:
        mptoken_issuance_id: The hex-encoded MPTokenIssuanceID.
        address: A classic XRPL address to test.

    Returns:
        ``True`` if ``address`` decodes to the issuer AccountID, else ``False``.
    """
    if len(mptoken_issuance_id) < _ISSUER_HEX_END:
        return False
    try:
        account_id = decode_classic_address(address)
    except (ValueError, KeyError, XRPLAddressCodecException):
        return False
    issuer_hex = mptoken_issuance_id[_ISSUER_HEX_START:_ISSUER_HEX_END]
    return issuer_hex.lower() == account_id.hex().lower()
