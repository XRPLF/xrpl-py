"""Model for MPTokenIssuanceSet transaction type."""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Final, Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import (
    HEX_REGEX,
    MAX_MPTOKEN_METADATA_LENGTH,
    MPT_META_WARNING_HEADER,
)

_MAX_TRANSFER_FEE: Final[int] = 50000


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


class MPTokenIssuanceSetMutableFlag(int, Enum):
    """
    MutableFlags for MPTokenIssuanceSet transaction.
    These flags enable MPT issuance flags that were declared mutable during
    MPTokenIssuanceCreate. They are one-way: once enabled, the corresponding
    capability cannot be disabled by MPTokenIssuanceSet.
    Prefixed with TMF (Transaction Mutable Flag).
    """

    TMF_MPT_SET_CAN_LOCK = 0x00000001
    """
    Sets the lsfMPTCanLock flag. Enables the token to be locked both
    individually and globally.
    """

    TMF_MPT_SET_REQUIRE_AUTH = 0x00000002
    """Sets the lsfMPTRequireAuth flag. Requires individual holders to be authorized."""

    TMF_MPT_SET_CAN_ESCROW = 0x00000004
    """Sets the lsfMPTCanEscrow flag. Allows holders to place balances into escrow."""

    TMF_MPT_SET_CAN_TRADE = 0x00000008
    """
    Sets the lsfMPTCanTrade flag. Allows holders to trade balances on
    the XRPL DEX.
    """

    TMF_MPT_SET_CAN_TRANSFER = 0x00000010
    """
    Sets the lsfMPTCanTransfer flag. Allows tokens to be transferred to
    non-issuer accounts.
    """

    TMF_MPT_SET_CAN_CLAWBACK = 0x00000020
    """
    Sets the lsfMPTCanClawback flag. Enables the issuer to claw back
    tokens via Clawback or AMMClawback transactions.
    """


class MPTokenIssuanceSetFlagInterface(TransactionFlagInterface):
    """
    Transactions of the MPTokenIssuanceSet type support additional values in the
    Flags field.
    This TypedDict represents those options.
    """

    TF_MPT_LOCK: bool
    TF_MPT_UNLOCK: bool


@dataclass(frozen=True, kw_only=True)
class MPTokenIssuanceSet(Transaction):
    """
    The MPTokenIssuanceSet transaction is used to globally lock/unlock a
    MPTokenIssuance, or lock/unlock an individual's MPToken.

    With the DynamicMPT amendment, this transaction can also be used to update
    fields (MPTokenMetadata, TransferFee) or enable MPT issuance flags that were
    marked as mutable during MPTokenIssuanceCreate.
    """

    mptoken_issuance_id: str = REQUIRED
    """Identifies the MPTokenIssuance"""

    holder: Optional[str] = None
    """
    An optional XRPL Address of an individual token holder balance to lock/unlock.
    If omitted, this transaction will apply to all any accounts holding MPTs.
    """

    mptoken_metadata: Optional[str] = None
    """
    New metadata to replace the existing value. Only valid if the MPTokenIssuance
    was created with TMF_MPT_CAN_MUTATE_METADATA flag set.
    Setting an empty string removes the field.
    Requires DynamicMPT amendment.
    """

    transfer_fee: Optional[int] = None
    """
    New transfer fee value. Only valid if the MPTokenIssuance was created with
    TMF_MPT_CAN_MUTATE_TRANSFER_FEE flag set.
    Setting to zero removes the field.
    Requires DynamicMPT amendment.
    """

    mutable_flags: Optional[int] = None
    """
    Enable MPT issuance flags that were marked as mutable during creation.
    These flags are one-way: once enabled, they cannot be disabled.
    Use MPTokenIssuanceSetMutableFlag enum values.
    Requires DynamicMPT amendment.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.MPTOKEN_ISSUANCE_SET,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        # Original validation for lock/unlock flags
        if self.has_flag(MPTokenIssuanceSetFlag.TF_MPT_LOCK) and self.has_flag(
            MPTokenIssuanceSetFlag.TF_MPT_UNLOCK
        ):
            errors["flags"] = (
                "flag conflict: both TF_MPT_LOCK and TF_MPT_UNLOCK can't be set"
            )

        # DynamicMPT validations
        has_dynamic_fields = (
            self.mutable_flags is not None
            or self.mptoken_metadata is not None
            or self.transfer_fee is not None
        )

        # Check for malformed combinations with holder field
        if has_dynamic_fields and self.holder is not None:
            errors["holder"] = (
                "holder cannot be provided when mutable_flags, mptoken_metadata, "
                "or transfer_fee is present"
            )

        # Check for malformed combinations with Flags field
        if has_dynamic_fields and self.flags is not None:
            # Flags cannot be used with DynamicMPT fields
            if self.flags != 0:
                errors["flags"] = (
                    "Flags cannot be provided when mutable_flags, "
                    "mptoken_metadata, or transfer_fee is present"
                )

        # Validate mutable_flags
        if self.mutable_flags is not None:
            # Check for invalid value (0 is invalid)
            if self.mutable_flags == 0:
                errors["mutable_flags"] = "mutable_flags cannot be 0"

            # Validate only known bits are used
            valid_mask = (
                MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK.value
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_REQUIRE_AUTH.value
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_ESCROW.value
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_TRADE.value
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_TRANSFER.value
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_CLAWBACK.value
            )
            if self.mutable_flags & ~valid_mask:
                errors["mutable_flags"] = "mutable_flags contains invalid bits"

        # Validate transfer_fee
        if self.transfer_fee is not None:
            if self.transfer_fee < 0 or self.transfer_fee > _MAX_TRANSFER_FEE:
                errors["transfer_fee"] = (
                    f"transfer_fee must be between 0 and {_MAX_TRANSFER_FEE}"
                )

        # Validate mptoken_metadata
        if self.mptoken_metadata is not None:
            # Empty string is allowed (removes the field)
            if len(self.mptoken_metadata) > 0:
                if len(self.mptoken_metadata) > MAX_MPTOKEN_METADATA_LENGTH:
                    errors["mptoken_metadata"] = (
                        "Metadata must be a hex string less than 1024 bytes "
                        "(alternatively, 2048 hex characters)."
                    )
                elif not HEX_REGEX.fullmatch(self.mptoken_metadata):
                    errors["mptoken_metadata"] = "Metadata must be a valid hex string"

                # Validate metadata format with warnings
                # Lazy import to avoid circular dependency
                from xrpl.utils.mptoken_metadata import validate_mptoken_metadata

                validation_messages = validate_mptoken_metadata(self.mptoken_metadata)
                if len(validation_messages) > 0:
                    message = "\n".join(
                        [MPT_META_WARNING_HEADER]
                        + [f"- {msg}" for msg in validation_messages]
                    )
                    warnings.warn(message, stacklevel=5)

        return errors
