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

    fee_amount: Optional[Amount] = None
    """The fee amount to be sponsored."""

    max_fee: Optional[Amount] = None
    """The maximum fee that can be sponsored."""

    remaining_owner_count: Optional[int] = None
    """The number of owner reserves (object reserves) the sponsor will cover.
    Serialized as the ``RemainingOwnerCount`` field (``sfRemainingOwnerCount``)."""

    transaction_type: TransactionType = field(
        default=TransactionType.SPONSORSHIP_SET,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        # ── Concern 2: exactly one of counterparty_sponsor / sponsee ──────────
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

        # ── Concern 3: mutually exclusive flag pairs ───────────────────────────
        if set_fee and clear_fee:
            errors["flags"] = (
                "`TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE` and "
                "`TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE` are mutually exclusive."
            )
        if set_res and clear_res:
            errors["flags"] = (
                "`TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE`"
                " and "
                "`TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE`"
                " are mutually exclusive."
            )
        if delete_obj and (set_fee or clear_fee or set_res or clear_res):
            errors["flags"] = (
                "`TF_DELETE_OBJECT` cannot be combined with any set/clear flags."
            )

        # ── Concern 4: counterparty_sponsor is only valid when deleting ───────
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

        if delete_obj:
            # C++ preflight: FeeAmount / MaxFee / RemainingOwnerCount must not be
            # present when deleting the Sponsorship object.
            forbidden = [
                name
                for name, value in (
                    ("fee_amount", self.fee_amount),
                    ("max_fee", self.max_fee),
                    ("remaining_owner_count", self.remaining_owner_count),
                )
                if value is not None
            ]
            if forbidden:
                errors["delete_object"] = (
                    "When `TF_DELETE_OBJECT` is active, the following fields must "
                    f"not be set: {', '.join(f'`{name}`' for name in forbidden)}."
                )
        else:
            # ── Concern 1: fee_amount / max_fee must be XRP (not IOU) ──────────
            # C++: if (!isXRP(amount)) return temBAD_AMOUNT  (only for non-delete)
            if self.fee_amount is not None and not isinstance(self.fee_amount, str):
                errors["fee_amount"] = (
                    "`fee_amount` must be XRP drops (a string), "
                    "not an issued currency or MPT amount."
                )
            if self.max_fee is not None and not isinstance(self.max_fee, str):
                errors["max_fee"] = (
                    "`max_fee` must be XRP drops (a string), "
                    "not an issued currency or MPT amount."
                )

        return errors
