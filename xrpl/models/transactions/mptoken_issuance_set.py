"""Model for MPTokenIssuanceSet transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init

ELGAMAL_PUBLIC_KEY_LENGTH = 33 * 2


class MPTokenIssuanceSetFlag(int, Enum):
    """
    Transactions of the MPTokenIssuanceSet type support additional values in the
    Flags field.
    This enum represents those options.
    """

    TF_MPT_LOCK = 0x00000001
    """
    If set, indicates that the MPT can be locked both individually and globally.
    If not set, the MPT cannot be locked in any way.
    """

    TF_MPT_UNLOCK = 0x00000002
    """
    If set, indicates that the MPT can be unlocked both individually and globally.
    If not set, the MPT cannot be unlocked in any way.
    """


class MPTokenIssuanceSetFlagInterface(TransactionFlagInterface):
    """
    Transactions of the MPTokenIssuanceSet type support additional values in the
    Flags field.
    This TypedDict represents those options.
    """

    TF_MPT_LOCK: bool
    TF_MPT_UNLOCK: bool


@require_kwargs_on_init
@dataclass(frozen=True)
class MPTokenIssuanceSet(Transaction):
    """
    The MPTokenIssuanceSet transaction is used to globally lock/unlock a
    MPTokenIssuance, or lock/unlock an individual's MPToken.
    """

    mptoken_issuance_id: str = REQUIRED
    """Identifies the MPTokenIssuance"""

    holder: Optional[str] = None
    """
    An optional XRPL Address of an individual token holder balance to lock/unlock.
    If omitted, this transaction will apply to all any accounts holding MPTs.
    """

    issuer_elgamal_public_key: Optional[str] = None
    """
    The EC-ElGamal public key used for the issuer's mirror balances.
    Can be 33 bytes (66 hex chars, compressed) or 64 bytes (128 hex chars, uncompressed).
    """

    auditor_elgamal_public_key: Optional[str] = None
    """
    The EC-ElGamal public key used for regulatory oversight (if applicable).
    Can be 33 bytes (66 hex chars, compressed) or 64 bytes (128 hex chars, uncompressed).
    """

    transaction_type: TransactionType = field(
        default=TransactionType.MPTOKEN_ISSUANCE_SET,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.has_flag(MPTokenIssuanceSetFlag.TF_MPT_LOCK) and self.has_flag(
            MPTokenIssuanceSetFlag.TF_MPT_UNLOCK
        ):
            errors["flags"] = (
                "flag conflict: both TF_MPT_LOCK and TF_MPT_UNLOCK can't be set"
            )

        has_issuer_key = (
            hasattr(self, "issuer_elgamal_public_key")
            and self.issuer_elgamal_public_key is not None
        )
        has_auditor_key = (
            hasattr(self, "auditor_elgamal_public_key")
            and self.auditor_elgamal_public_key is not None
        )

        if has_issuer_key and self.issuer_elgamal_public_key is not None:
            key_len = len(self.issuer_elgamal_public_key)
            # Accept compressed (33 bytes = 66 hex) or uncompressed (64 bytes = 128 hex)
            if key_len not in [66, 128]:
                errors["issuer_elgamal_public_key"] = (
                    "issuer_elgamal_public_key must be 33 bytes (66 hex characters, "
                    "compressed) or 64 bytes (128 hex characters, uncompressed)"
                )

        if has_auditor_key and self.auditor_elgamal_public_key is not None:
            key_len = len(self.auditor_elgamal_public_key)
            # Accept compressed (33 bytes = 66 hex) or uncompressed (64 bytes = 128 hex)
            if key_len not in [66, 128]:
                errors["auditor_elgamal_public_key"] = (
                    "auditor_elgamal_public_key must be 33 bytes (66 hex characters, "
                    "compressed) or 64 bytes (128 hex characters, uncompressed)"
                )

        if has_auditor_key and not has_issuer_key:
            errors["auditor_elgamal_public_key"] = (
                "auditor_elgamal_public_key requires issuer_elgamal_public_key"
            )

        if (
            hasattr(self, "holder")
            and self.holder is not None
            and (has_issuer_key or has_auditor_key)
        ):
            errors["holder"] = (
                "Cannot mutate privacy fields while also acting as a Holder"
            )

        return errors
