"""Model for MPTokenIssuanceSet transaction type."""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Final, Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.mptoken_issuance_create import (
    MPTokenIssuanceImmutableFlag,
)
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import (
    HEX_REGEX,
    MAX_MPTOKEN_METADATA_LENGTH,
    MPT_META_WARNING_HEADER,
    validate_domain_id,
)

_MAX_TRANSFER_FEE: Final[int] = 50000

ENCRYPTION_KEY_LENGTH = 33 * 2


class MPTokenIssuanceSetFlag(int, Enum):
    """
    Transactions of the MPTokenIssuanceSet type support additional values in the
    Flags field. This enum represents those options.

    With the DynamicMPT amendment, the capability-setting flags (TF_MPT_SET_*)
    enable the corresponding MPT issuance flag on the MPTokenIssuance. These flags
    are one-way: once set, a capability cannot be unset by MPTokenIssuanceSet.
    """

    TF_MPT_LOCK = 0x00000001
    """
    If set, indicates that the MPT can be locked both individually and globally.
    """

    TF_MPT_UNLOCK = 0x00000002
    """
    If set, indicates that the MPT can be unlocked both individually and globally.
    """

    TF_MPT_SET_CAN_LOCK = 0x00000004
    """
    Sets the lsfMPTCanLock flag. Enables the token to be locked both
    individually and globally.
    """

    TF_MPT_SET_REQUIRE_AUTH = 0x00000008
    """
    Sets the lsfMPTRequireAuth flag. Requires individual holders to be
    authorized.
    """

    TF_MPT_SET_CAN_ESCROW = 0x00000010
    """
    Sets the lsfMPTCanEscrow flag. Allows holders to place balances into escrow.
    """

    TF_MPT_SET_CAN_TRADE = 0x00000020
    """
    Sets the lsfMPTCanTrade flag. Allows holders to trade balances on the
    XRPL DEX.
    """

    TF_MPT_SET_CAN_TRANSFER = 0x00000040
    """
    Sets the lsfMPTCanTransfer flag. Allows tokens to be transferred to
    non-issuer accounts.
    """

    TF_MPT_SET_CAN_CLAWBACK = 0x00000080
    """
    Sets the lsfMPTCanClawback flag. Enables the issuer to claw back tokens via
    Clawback or AMMClawback transactions.
    """

    TF_MPT_SET_CAN_HOLD_CONFIDENTIAL_BALANCE = 0x00000100
    """
    Sets the lsfMPTCanHoldConfidentialBalance flag. Enables the token to be held
    in a confidential balance. Requires the XLS-96 Confidential MPT amendment.
    """


# The capability-setting flags within the Flags field (used to detect whether a
# transaction is mutating the issuance rather than locking/unlocking it).
_CAPABILITY_SET_FLAGS: Final = (
    MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK,
    MPTokenIssuanceSetFlag.TF_MPT_SET_REQUIRE_AUTH,
    MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_ESCROW,
    MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_TRADE,
    MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_TRANSFER,
    MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_CLAWBACK,
    MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_HOLD_CONFIDENTIAL_BALANCE,
)


class MPTokenIssuanceSetFlagInterface(TransactionFlagInterface):
    """
    Transactions of the MPTokenIssuanceSet type support additional values in the
    Flags field. This TypedDict represents those options.
    """

    TF_MPT_LOCK: bool
    TF_MPT_UNLOCK: bool
    TF_MPT_SET_CAN_LOCK: bool
    TF_MPT_SET_REQUIRE_AUTH: bool
    TF_MPT_SET_CAN_ESCROW: bool
    TF_MPT_SET_CAN_TRADE: bool
    TF_MPT_SET_CAN_TRANSFER: bool
    TF_MPT_SET_CAN_CLAWBACK: bool
    TF_MPT_SET_CAN_HOLD_CONFIDENTIAL_BALANCE: bool


@dataclass(frozen=True, kw_only=True)
class MPTokenIssuanceSet(Transaction):
    """
    The MPTokenIssuanceSet transaction is used to globally lock/unlock a
    MPTokenIssuance, or lock/unlock an individual's MPToken.

    It can also register confidential encryption keys and enable the confidential
    amount feature (XLS-0096).

    With the DynamicMPT amendment, this transaction can also update
    MPTokenMetadata and TransferFee, enable MPT issuance flags (via the
    TF_MPT_SET_* capability flags in the Flags field), and permanently make
    fields or flags immutable via ImmutableFlags.
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

    domain_id: Optional[str] = None
    """
    The DomainID of a Permissioned Domain to associate with this MPTokenIssuance,
    as a 64-character hex string.
    """

    mptoken_metadata: Optional[str] = None
    """
    New metadata to replace the existing value. Rejected if MPTokenMetadata was
    made immutable via ImmutableFlags. Setting an empty string removes the field.
    Requires the DynamicMPT amendment.
    """

    transfer_fee: Optional[int] = None
    """
    New transfer fee value. Rejected if TransferFee was made immutable via
    ImmutableFlags. Setting to zero removes the field.
    Requires the DynamicMPT amendment.
    """

    immutable_flags: Optional[int] = None
    """
    Permanently makes specific fields or flags immutable. Bits set here are added
    to (not replacing) the issuance's existing ImmutableFlags; once a bit is set,
    the corresponding field or flag can never be modified again.
    Use MPTokenIssuanceImmutableFlag enum values.
    Requires the DynamicMPT amendment.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.MPTOKEN_ISSUANCE_SET,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        is_lock = self.has_flag(MPTokenIssuanceSetFlag.TF_MPT_LOCK)
        is_unlock = self.has_flag(MPTokenIssuanceSetFlag.TF_MPT_UNLOCK)

        # Lock/unlock flag conflict (base MPTokenIssuanceSet behavior).
        if is_lock and is_unlock:
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

        if self.domain_id is not None:
            err = validate_domain_id(self.domain_id)
            if err:
                errors["domain_id"] = err

        # domain_id and holder are mutually exclusive.
        if self.domain_id is not None and self.holder is not None:
            errors["domain_id_holder"] = "domain_id and holder cannot both be set"

        # A transaction "mutates the issuance" if it sets any capability flag,
        # updates metadata / transfer_fee, or declares immutability.
        has_capability_flag = any(self.has_flag(f) for f in _CAPABILITY_SET_FLAGS)
        is_mutate = (
            has_capability_flag
            or self.mptoken_metadata is not None
            or self.transfer_fee is not None
            or self.immutable_flags is not None
        )

        # Holder is not allowed alongside a mutate-issuance operation.
        if is_mutate and self.holder is not None:
            errors["holder"] = (
                "holder cannot be provided when setting capability flags, "
                "mptoken_metadata, transfer_fee, or immutable_flags"
            )

        # tfMPTLock/tfMPTUnlock cannot be combined with a mutate operation.
        if is_mutate and (is_lock or is_unlock):
            errors["lock_unlock_mutate"] = (
                "TF_MPT_LOCK/TF_MPT_UNLOCK cannot be combined with capability "
                "flags, mptoken_metadata, transfer_fee, or immutable_flags"
            )

        # Validate immutable_flags bitmask.
        if self.immutable_flags is not None:
            valid_mask = 0
            for flag in MPTokenIssuanceImmutableFlag:
                valid_mask |= flag.value

            if self.immutable_flags == 0:
                errors["immutable_flags"] = "immutable_flags cannot be 0"
            elif self.immutable_flags & ~valid_mask:
                errors["immutable_flags"] = (
                    "immutable_flags contains invalid or reserved bits"
                )

        # Validate transfer_fee.
        if self.transfer_fee is not None and (
            self.transfer_fee < 0 or self.transfer_fee > _MAX_TRANSFER_FEE
        ):
            errors["transfer_fee"] = (
                f"transfer_fee must be between 0 and {_MAX_TRANSFER_FEE}"
            )

        # Validate mptoken_metadata (an empty string removes the field).
        if self.mptoken_metadata is not None and len(self.mptoken_metadata) > 0:
            if len(self.mptoken_metadata) > MAX_MPTOKEN_METADATA_LENGTH:
                errors["mptoken_metadata"] = (
                    "Metadata must be a hex string less than 1024 bytes "
                    "(alternatively, 2048 hex characters)."
                )
            elif not HEX_REGEX.fullmatch(self.mptoken_metadata):
                errors["mptoken_metadata"] = "Metadata must be a valid hex string"
            else:
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
