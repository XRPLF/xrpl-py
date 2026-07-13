"""Model for MPTokenIssuanceSet transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType

ENCRYPTION_KEY_LENGTH = 33 * 2


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


class MPTokenIssuanceSetMutableFlag(int, Enum):
    """
    Bit flags for the MutableFlags field on MPTokenIssuanceSet transactions.
    Enables the lsfMPTCanHoldConfidentialBalance flag post-issuance.
    The sfMutableFlags field requires the DynamicMPT amendment.
    """

    TMF_MPT_SET_CAN_HOLD_CONFIDENTIAL_BALANCE = 0x00000040
    """
    Sets the lsfMPTCanHoldConfidentialBalance flag on the issuance, enabling
    confidential transfers. Only valid if
    lsmfMPTCannotEnableCanHoldConfidentialBalance is not set. Enabling is
    one-way: there is no flag to clear it once set.
    Requires the ConfidentialTransfer amendment.
    """


@dataclass(frozen=True, kw_only=True)
class MPTokenIssuanceSet(Transaction):
    """
    The MPTokenIssuanceSet transaction is used to globally lock/unlock a
    MPTokenIssuance, lock/unlock an individual's MPToken, register encryption
    keys, and enable/disable the confidential amount feature.
    """

    mptoken_issuance_id: str = REQUIRED
    """Identifies the MPTokenIssuance"""

    holder: Optional[str] = None
    """
    An optional XRPL Address of an individual token holder balance to lock/unlock.
    If omitted, this transaction will apply to all any accounts holding MPTs.
    """

    issuer_encryption_key: Optional[str] = None
    """
    The 33-byte EC-ElGamal public key used for the issuer's mirror balances.
    """

    auditor_encryption_key: Optional[str] = None
    """
    The 33-byte EC-ElGamal public key used for regulatory oversight (if applicable).
    """

    mutable_flags: Optional[int] = None
    """
    Bit flags to toggle mutable issuance properties. Used to enable or disable
    the confidential amount feature post-issuance.
    See MPTokenIssuanceSetMutableFlag for available values.
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
            hasattr(self, "issuer_encryption_key")
            and self.issuer_encryption_key is not None
        )
        has_auditor_key = (
            hasattr(self, "auditor_encryption_key")
            and self.auditor_encryption_key is not None
        )

        if has_issuer_key and self.issuer_encryption_key is not None:
            key_len = len(self.issuer_encryption_key)
            if key_len != ENCRYPTION_KEY_LENGTH:
                errors["issuer_encryption_key"] = (
                    "issuer_encryption_key must be 33 bytes (66 hex characters)"
                )

        if has_auditor_key and self.auditor_encryption_key is not None:
            key_len = len(self.auditor_encryption_key)
            if key_len != ENCRYPTION_KEY_LENGTH:
                errors["auditor_encryption_key"] = (
                    "auditor_encryption_key must be 33 bytes (66 hex characters)"
                )

        if has_auditor_key and not has_issuer_key:
            errors["auditor_encryption_key"] = (
                "auditor_encryption_key requires issuer_encryption_key"
            )

        if (
            hasattr(self, "holder")
            and self.holder is not None
            and (has_issuer_key or has_auditor_key)
        ):
            errors["holder"] = (
                "Cannot mutate confidential fields while also acting as a Holder"
            )

        return errors
