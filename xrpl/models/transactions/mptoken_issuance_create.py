"""Model for MPTokenIssuanceCreate transaction type."""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Final, Self

from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import (
    HEX_REGEX,
    MAX_MPTOKEN_METADATA_LENGTH,
    MPT_META_WARNING_HEADER,
    validate_domain_id,
)

_MAX_TRANSFER_FEE: Final[int] = 50000


class MPTokenIssuanceCreateFlag(int, Enum):
    """
    Transactions of the MPTokenIssuanceCreate type support additional values in the
    Flags field.
    This enum represents those options.
    """

    TF_MPT_CAN_LOCK = 0x00000002
    TF_MPT_REQUIRE_AUTH = 0x00000004
    TF_MPT_CAN_ESCROW = 0x00000008
    TF_MPT_CAN_TRADE = 0x00000010
    TF_MPT_CAN_TRANSFER = 0x00000020
    TF_MPT_CAN_CLAWBACK = 0x00000040
    TF_MPT_CAN_HOLD_CONFIDENTIAL_BALANCE = 0x00000080
    """
    If set, indicates that the MPT can hold confidential balances.
    This flag must be set to enable confidential MPT functionality.
    """


class MPTokenIssuanceImmutableFlag(int, Enum):
    """
    ImmutableFlags for the MPTokenIssuance ledger object (XLS-94d DynamicMPT).
    Under DynamicMPT, MPTokenMetadata, TransferFee, and the MPT issuance flags
    are mutable by default; setting a bit here permanently makes the corresponding
    field or flag immutable. Once set, it can never be modified again.
    Shared by MPTokenIssuanceCreate and MPTokenIssuanceSet.
    Prefixed with TIF (Transaction Immutable Flag).
    """

    TIF_MPT_CAN_LOCK = 0x00000002
    """Makes flag lsfMPTCanLock immutable"""

    TIF_MPT_REQUIRE_AUTH = 0x00000004
    """Makes flag lsfMPTRequireAuth immutable"""

    TIF_MPT_CAN_ESCROW = 0x00000008
    """Makes flag lsfMPTCanEscrow immutable"""

    TIF_MPT_CAN_TRADE = 0x00000010
    """Makes flag lsfMPTCanTrade immutable"""

    TIF_MPT_CAN_TRANSFER = 0x00000020
    """Makes flag lsfMPTCanTransfer immutable"""

    TIF_MPT_CAN_CLAWBACK = 0x00000040
    """Makes flag lsfMPTCanClawback immutable"""

    TIF_MPT_CAN_HOLD_CONFIDENTIAL_BALANCE = 0x00000080
    """
    Makes flag lsfMPTCanHoldConfidentialBalance immutable.
    Requires the XLS-96 Confidential MPT amendment.
    """

    TIF_MPT_METADATA = 0x00010000
    """Makes field MPTokenMetadata immutable"""

    TIF_MPT_TRANSFER_FEE = 0x00020000
    """Makes field TransferFee immutable"""


class MPTokenIssuanceCreateFlagInterface(TransactionFlagInterface):
    """
    Transactions of the MPTokenIssuanceCreate type support additional values in the
    Flags field.
    This TypedDict represents those options.
    """

    TF_MPT_CAN_LOCK: bool
    TF_MPT_REQUIRE_AUTH: bool
    TF_MPT_CAN_ESCROW: bool
    TF_MPT_CAN_TRADE: bool
    TF_MPT_CAN_TRANSFER: bool
    TF_MPT_CAN_CLAWBACK: bool
    TF_MPT_CAN_HOLD_CONFIDENTIAL_BALANCE: bool


@dataclass(frozen=True, kw_only=True)
class MPTokenIssuanceCreate(Transaction):
    """
    The MPTokenIssuanceCreate transaction creates a MPTokenIssuance object
    and adds it to the relevant directory node of the creator account.
    This transaction is the only opportunity an issuer has to specify any token fields
    that are defined as immutable (e.g., MPT Flags). If the transaction is successful,
    the newly created token will be owned by the account (the creator account) which
    executed the transaction.
    """

    asset_scale: Optional[int] = None
    """
    An asset scale is the difference, in orders of magnitude, between a standard unit
    and a corresponding fractional unit. More formally, the asset scale is a
    non-negative integer (0, 1, 2, …) such that one standard unit equals 10^(-scale) of
    a corresponding fractional unit. If the fractional unit equals the standard unit,
    then the asset scale is 0.
    Note that this value is optional, and will default to 0 if not supplied.
    """

    maximum_amount: Optional[str] = None
    """
    Specifies the maximum asset amount of this token that should ever be issued.
    It is a non-negative integer string that can store a range of up to 63 bits. If
    not set, the max amount will default to the largest unsigned 63-bit integer
    (0x7FFFFFFFFFFFFFFF)
    """

    transfer_fee: Optional[int] = None
    """
    Specifies the fee to charged by the issuer for secondary sales of the Token,
    if such sales are allowed. Valid values for this field are between 0 and 50,000
    inclusive, allowing transfer rates of between 0.000% and 50.000% in increments of
    0.001. The field must NOT be present if the `tfMPTCanTransfer` flag is not set.
    """

    mptoken_metadata: Optional[str] = None
    """
    Arbitrary metadata about this issuance, in hex format, limited to 1024 bytes.
    Use `encode_mptoken_metadata` to convert from a JSON object to this format.
    Use `decode_mptoken_metadata` to convert from this format to a JSON object.

    While adherence to the XLS-89d format is not mandatory, non-compliant metadata
    may not be discoverable by ecosystem tools such as explorers and indexers.
    """

    domain_id: Optional[str] = None
    """
    The DomainID of a Permissioned Domain to associate with this MPTokenIssuance,
    as a 64-character hex string.
    """

    immutable_flags: Optional[int] = None
    """
    Permanently makes specific fields or flags immutable. Under DynamicMPT,
    MPTokenMetadata, TransferFee, and the MPT issuance flags are mutable by
    default; setting a bit here makes the corresponding field/flag immutable
    for the life of the issuance.
    This field is optional and only available when the DynamicMPT amendment is enabled.
    Use MPTokenIssuanceImmutableFlag enum values.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.MPTOKEN_ISSUANCE_CREATE,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.transfer_fee is not None:
            if not self.has_flag(MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER):
                errors["transfer_fee"] = (
                    "Field cannot be provided without enabling tfMPTCanTransfer flag."
                )
            if self.transfer_fee < 0 or self.transfer_fee > _MAX_TRANSFER_FEE:
                errors["transfer_fee"] = "Field must be between 0 and " + str(
                    _MAX_TRANSFER_FEE
                )

        if self.mptoken_metadata is not None and (
            len(self.mptoken_metadata) == 0
            or len(self.mptoken_metadata) > MAX_MPTOKEN_METADATA_LENGTH
            or not HEX_REGEX.fullmatch(self.mptoken_metadata)
        ):
            errors["mptoken_metadata"] = (
                "Metadata must be valid non-empty hex string less than 1024 bytes "
                "(alternatively, 2048 hex characters)."
            )

        if self.mptoken_metadata is not None:
            # Lazy import to avoid circular dependency
            from xrpl.utils.mptoken_metadata import validate_mptoken_metadata

            validation_messages = validate_mptoken_metadata(self.mptoken_metadata)

            if len(validation_messages) > 0:
                message = "\n".join(
                    [MPT_META_WARNING_HEADER]
                    + [f"- {msg}" for msg in validation_messages]
                )
                warnings.warn(message, stacklevel=5)

        if self.domain_id is not None:
            err = validate_domain_id(self.domain_id)
            if err:
                errors["domain_id"] = err

        # Validate immutable_flags (DynamicMPT)
        if self.immutable_flags is not None:
            # A present ImmutableFlags must be non-zero and use only known bits
            # (the reserved 0x00000001 is not a valid ImmutableFlags bit).
            valid_mask = 0
            for flag in MPTokenIssuanceImmutableFlag:
                valid_mask |= flag.value

            # The zero case needs its own check: `0 & ~valid_mask` is 0 (falsy),
            # so the invalid-bits check below would let it through. Zero has no
            # bits set, meaning nothing is declared immutable, which is a
            # pointless no-op we reject explicitly.
            if self.immutable_flags == 0:
                errors["immutable_flags"] = "immutable_flags cannot be 0"
            elif self.immutable_flags & ~valid_mask:
                errors["immutable_flags"] = (
                    "immutable_flags contains invalid or reserved bits"
                )

        return errors
