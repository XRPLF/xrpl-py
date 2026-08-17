"""Model for SponsorshipSet transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.amounts import Amount
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType


class SponsorshipSetFlag(int, Enum):
    """
    Enum for SponsorshipSet Transaction Flags.

    Transactions of the SponsorshipSet type support additional values in the
    Flags field. This enum represents those options.
    """

    TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE = 0x00010000
    """Set the lsfSponsorshipRequireSignForFee flag on the Sponsorship object."""

    TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE = 0x00020000
    """Clear the lsfSponsorshipRequireSignForFee flag on the Sponsorship object."""

    TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE = 0x00040000
    """Set the lsfSponsorshipRequireSignForReserve flag on the Sponsorship object."""

    TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE = 0x00080000
    """Clear the lsfSponsorshipRequireSignForReserve flag on the Sponsorship object."""

    TF_DELETE_OBJECT = 0x00100000
    """Delete the Sponsorship object."""


class SponsorshipSetFlagInterface(TransactionFlagInterface):
    """
    Transactions of the SponsorshipSet type support additional values in the
    Flags field. This TypedDict represents those options.
    """

    TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE: bool
    TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE: bool
    TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE: bool
    TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE: bool
    TF_DELETE_OBJECT: bool


@dataclass(frozen=True, kw_only=True)
class SponsorshipSet(Transaction):
    """
    Represents a SponsorshipSet transaction, which creates or modifies
    sponsorship objects on the XRP Ledger.
    """

    counterparty_sponsor: Optional[str] = None
    """The account that is the counterparty sponsor."""

    sponsee: Optional[str] = None
    """The account that is being sponsored."""

    fee_amount_delta: Optional[Amount] = None
    """The *change* to apply to the sponsorship's fee budget, in XRP drops.

    Serialized as ``FeeAmountDelta`` (``sfFeeAmountDelta``). A positive value
    moves XRP from the sponsor's balance into the object's ``FeeAmount``; a
    negative value refunds it, clamped so the budget cannot go below zero. Must
    be non-zero, and must be positive when creating the object.
    """

    max_fee: Optional[Amount] = None
    """The maximum fee that can be sponsored. An absolute value, not a delta."""

    remaining_owner_count_delta: Optional[int] = None
    """The *change* to apply to the sponsored owner-reserve budget.

    Serialized as ``RemainingOwnerCountDelta``
    (``sfRemainingOwnerCountDelta``), a signed 32-bit integer. Negative values
    reduce the budget, clamped at zero. Must be non-zero, and must be positive
    when creating the object.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.SPONSORSHIP_SET,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        # ── Exactly one of counterparty_sponsor / sponsee ─────────────────────
        has_counterparty = self.counterparty_sponsor is not None
        has_sponsee = self.sponsee is not None

        if has_counterparty == has_sponsee:  # neither or both
            errors["counterparty_sponsor"] = (
                "Exactly one of `counterparty_sponsor` or `sponsee` must be present "
                "(not both, not neither)."
            )
        elif has_counterparty and self.counterparty_sponsor == self.account:
            errors["counterparty_sponsor"] = (
                "`counterparty_sponsor` must differ from `account`."
            )
        elif has_sponsee and self.sponsee == self.account:
            errors["sponsee"] = "`sponsee` must differ from `account`."

        # Determine effective flags for the remaining checks.
        # has_flag() handles None / int / list / dict safely.
        delete_obj = self.has_flag(int(SponsorshipSetFlag.TF_DELETE_OBJECT))
        set_fee = self.has_flag(
            int(SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE)
        )
        clear_fee = self.has_flag(
            int(SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE)
        )
        set_res = self.has_flag(
            int(SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE)
        )
        clear_res = self.has_flag(
            int(SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE)
        )

        # ── Mutually exclusive flag pairs ──────────────────────────────────────
        if set_fee and clear_fee:
            errors["flags_fee"] = (
                "`TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE` and "
                "`TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE` are mutually exclusive."
            )
        if set_res and clear_res:
            errors["flags_reserve"] = (
                "`TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE`"
                " and "
                "`TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE`"
                " are mutually exclusive."
            )
        if delete_obj and (set_fee or clear_fee or set_res or clear_res):
            errors["flags_delete"] = (
                "`TF_DELETE_OBJECT` cannot be combined with any set/clear flags."
            )

        # ── counterparty_sponsor is only valid when deleting ──────────────────
        # C++ preflight: only the sponsor (account == sponsor) may create/update a
        # sponsorship; either party may delete. Specifying `counterparty_sponsor`
        # means the submitter is the sponsee, which is only allowed for deletion.
        # Only flag this once the field is otherwise well-formed (exactly one of
        # counterparty_sponsor / sponsee, and it differs from `account`).
        if (
            has_counterparty
            and not has_sponsee
            and self.counterparty_sponsor != self.account
            and not delete_obj
        ):
            errors["counterparty_sponsor"] = (
                "`counterparty_sponsor` can only be used together with "
                "`TF_DELETE_OBJECT` (only the sponsor may create or update a "
                "sponsorship)."
            )

        modification_fields = (
            ("fee_amount_delta", self.fee_amount_delta),
            ("max_fee", self.max_fee),
            ("remaining_owner_count_delta", self.remaining_owner_count_delta),
        )

        if delete_obj:
            # C++ preflight: the modification fields must not be present when
            # deleting the Sponsorship object (temMALFORMED).
            forbidden = [
                name for name, value in modification_fields if value is not None
            ]
            if forbidden:
                errors["delete_object"] = (
                    "When `TF_DELETE_OBJECT` is active, the following fields must "
                    f"not be set: {', '.join(f'`{name}`' for name in forbidden)}."
                )
        else:
            # `fee_amount_delta` must be XRP and non-zero (temBAD_AMOUNT). It is a
            # delta, so a negative value is legal -- it refunds budget to the
            # sponsor -- but zero would be a no-op.
            if self.fee_amount_delta is not None:
                if not isinstance(self.fee_amount_delta, str):
                    errors["fee_amount_delta"] = (
                        "`fee_amount_delta` must be XRP drops (a string), "
                        "not an issued currency or MPT amount."
                    )
                else:
                    try:
                        fee_amount_delta_drops = int(self.fee_amount_delta)
                    except ValueError:
                        # A non-numeric string would otherwise raise a raw
                        # ValueError from int() instead of a clean model error.
                        errors["fee_amount_delta"] = (
                            "`fee_amount_delta` must be an integer string of "
                            "XRP drops."
                        )
                    else:
                        if fee_amount_delta_drops == 0:
                            errors["fee_amount_delta"] = (
                                "`fee_amount_delta` must be non-zero; it is a "
                                "change to apply to the fee budget, so zero has "
                                "no effect."
                            )

            # `max_fee` is an absolute cap, so it must be XRP and non-negative
            # (temBAD_AMOUNT).
            if self.max_fee is not None:
                if not isinstance(self.max_fee, str):
                    errors["max_fee"] = (
                        "`max_fee` must be XRP drops (a string), "
                        "not an issued currency or MPT amount."
                    )
                else:
                    try:
                        max_fee_drops = int(self.max_fee)
                    except ValueError:
                        errors["max_fee"] = (
                            "`max_fee` must be an integer string of XRP drops."
                        )
                    else:
                        if max_fee_drops < 0:
                            errors["max_fee"] = "`max_fee` must not be negative."

            # `remaining_owner_count_delta` must be non-zero (temINVALID) and fit
            # in a signed 32-bit integer
            if self.remaining_owner_count_delta is not None:
                if self.remaining_owner_count_delta == 0:
                    errors["remaining_owner_count_delta"] = (
                        "`remaining_owner_count_delta` must be non-zero; it is a "
                        "change to apply to the reserve budget, so zero has no "
                        "effect."
                    )
                elif not (-(2**31) <= self.remaining_owner_count_delta <= 2**31 - 1):
                    errors["remaining_owner_count_delta"] = (
                        "`remaining_owner_count_delta` must fit in a signed 32-bit "
                        "integer (-2147483648 to 2147483647)."
                    )

            # A transaction that neither carries a modification field nor sets a
            # sponsorship flag does nothing (temREDUNDANT).
            if all(value is None for _, value in modification_fields) and not (
                set_fee or clear_fee or set_res or clear_res
            ):
                errors["SponsorshipSet"] = (
                    "A `SponsorshipSet` that is not deleting must set at least "
                    "one of `fee_amount_delta`, `max_fee`, "
                    "`remaining_owner_count_delta`, or a sponsorship flag; "
                    "otherwise it has no effect."
                )

        return errors
