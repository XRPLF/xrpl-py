"""Model for SponsorshipSet transaction type and related flags."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class SponsorshipSetFlag(int, Enum):
    """Flags for SponsorshipSet transaction."""

    TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE = 0x00010000
    """
    Adds the restriction that every use of this sponsor for sponsoring fees
    requires a signature from the sponsor.
    """

    TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE = 0x00020000
    """
    Removes the restriction that every use of this sponsor for sponsoring fees
    requires a signature from the sponsor.
    """

    TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE = 0x00040000
    """
    Adds the restriction that every use of this sponsor for sponsoring reserves
    requires a signature from the sponsor.
    """

    TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE = 0x00080000
    """
    Removes the restriction that every use of this sponsor for sponsoring reserves
    requires a signature from the sponsor.
    """

    TF_DELETE_OBJECT = 0x00100000
    """Removes the Sponsorship ledger object."""


class SponsorshipSetFlagInterface(TransactionFlagInterface):
    """
    Transactions of the SponsorshipSet type support additional values in the Flags field.
    This TypedDict represents those options.
    """

    TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE: bool
    TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE: bool
    TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE: bool
    TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE: bool
    TF_DELETE_OBJECT: bool


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class SponsorshipSet(Transaction):
    """
    Represents a SponsorshipSet transaction, which creates, updates, and deletes
    the Sponsorship object.

    The Account sending the transaction may be either the sponsor or the sponsee.
    """

    sponsor: Optional[str] = None
    """
    The sponsor associated with this relationship. This account also pays for the
    reserve of this object. If this field is included, the Account is assumed to be
    the Sponsee.
    """

    sponsee: Optional[str] = None
    """
    The sponsee associated with this relationship. If this field is included, the
    Account is assumed to be the Sponsor.
    """

    fee_amount: Optional[str] = None
    """
    The (remaining) amount of XRP that the sponsor has provided for the sponsee to
    use for fees. This value will replace what is currently in the Sponsorship.FeeAmount
    field (if it exists).
    """

    max_fee: Optional[str] = None
    """
    The maximum fee per transaction that will be sponsored. This is to prevent
    abuse/excessive draining of the sponsored fee pool.
    """

    reserve_count: Optional[int] = None
    """
    The (remaining) amount of reserves that the sponsor has provided for the sponsee
    to use. This value will replace what is currently in the Sponsorship.ReserveCount
    field (if it exists).
    """

    transaction_type: TransactionType = field(
        default=TransactionType.SPONSORSHIP_SET,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        """
        Validate the SponsorshipSet transaction.

        Returns:
            A dictionary of field names to error messages.
        """
        errors = super()._get_errors()

        # Both Sponsor and Sponsee cannot be specified
        if self.sponsor is not None and self.sponsee is not None:
            errors["sponsor_sponsee"] = (
                "Both Sponsor and Sponsee cannot be specified. "
                "Specify only one to indicate the role of Account."
            )

        # Neither Sponsor nor Sponsee can be omitted
        if self.sponsor is None and self.sponsee is None:
            errors["sponsor_sponsee"] = (
                "Either Sponsor or Sponsee must be specified to indicate "
                "the role of Account."
            )

        # Account must be either Sponsor or Sponsee
        if self.sponsor is not None and self.account == self.sponsor:
            errors["account"] = (
                "Account cannot be the same as Sponsor. "
                "If Sponsor is specified, Account is assumed to be the Sponsee."
            )

        if self.sponsee is not None and self.account == self.sponsee:
            errors["account"] = (
                "Account cannot be the same as Sponsee. "
                "If Sponsee is specified, Account is assumed to be the Sponsor."
            )

        # Owner == Sponsee check (self-sponsorship)
        sponsor_account = self.sponsee if self.sponsee is not None else self.account
        sponsee_account = self.sponsor if self.sponsor is not None else self.account

        if sponsor_account == sponsee_account:
            errors["self_sponsorship"] = (
                "Cannot create self-sponsorship. "
                "Sponsor and Sponsee must be different accounts."
            )

        # Sponsor field specified means Sponsee is submitting
        # Only sponsor can create/update, so if Sponsor field is present and
        # tfDeleteObject is not enabled, it's an error
        if self.sponsor is not None:
            if self.flags is None or not (self.flags & SponsorshipSetFlag.TF_DELETE_OBJECT):
                errors["sponsor_field"] = (
                    "If Sponsor field is specified (Sponsee submitting), "
                    "tfDeleteObject flag must be enabled. "
                    "Only the sponsor can create/update the Sponsorship object."
                )

        # Validate tfDeleteObject flag restrictions
        if self.flags is not None and (self.flags & SponsorshipSetFlag.TF_DELETE_OBJECT):
            if self.fee_amount is not None:
                errors["fee_amount_with_delete"] = (
                    "FeeAmount cannot be specified when tfDeleteObject is enabled."
                )
            if self.max_fee is not None:
                errors["max_fee_with_delete"] = (
                    "MaxFee cannot be specified when tfDeleteObject is enabled."
                )
            if self.reserve_count is not None:
                errors["reserve_count_with_delete"] = (
                    "ReserveCount cannot be specified when tfDeleteObject is enabled."
                )

            # Check for conflicting flags
            conflicting_flags = [
                SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE,
                SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE,
                SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE,
                SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE,
            ]
            for flag in conflicting_flags:
                if self.flags & flag:
                    errors["invalid_flag_with_delete"] = (
                        "Cannot set or clear signature requirement flags "
                        "when tfDeleteObject is enabled."
                    )
                    break

        # Validate MaxFee
        if self.max_fee is not None:
            try:
                max_fee_value = int(self.max_fee)
                if max_fee_value < 0:
                    errors["max_fee"] = "MaxFee must be non-negative."
                # Note: Base fee validation would require network state
            except ValueError:
                errors["max_fee"] = "MaxFee must be a valid numeric string."

        # Validate FeeAmount
        if self.fee_amount is not None:
            try:
                fee_amount_value = int(self.fee_amount)
                if fee_amount_value < 0:
                    errors["fee_amount"] = "FeeAmount must be non-negative."

                # MaxFee cannot be greater than FeeAmount
                if self.max_fee is not None:
                    try:
                        max_fee_value = int(self.max_fee)
                        if max_fee_value > fee_amount_value:
                            errors["max_fee_exceeds_fee_amount"] = (
                                "MaxFee cannot be greater than FeeAmount."
                            )
                    except ValueError:
                        pass  # Already caught above
            except ValueError:
                errors["fee_amount"] = "FeeAmount must be a valid numeric string."

        # Validate ReserveCount
        if self.reserve_count is not None and self.reserve_count < 0:
            errors["reserve_count"] = "ReserveCount must be non-negative."

        return errors

