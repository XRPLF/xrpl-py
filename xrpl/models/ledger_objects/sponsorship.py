"""Model for Sponsorship ledger entry type."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.base_model import BaseModel
from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.required import REQUIRED
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class SponsorshipFlag(int, Enum):
    """Flags for Sponsorship ledger entries."""

    LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE = 0x00010000
    """If set, every use of this sponsor for sponsoring fees requires a signature from the sponsor."""

    LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE = 0x00020000
    """If set, every use of this sponsor for sponsoring reserves requires a signature from the sponsor."""


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Sponsorship(BaseModel):
    """
    Represents a Sponsorship ledger entry.

    A Sponsorship object describes a sponsorship relationship between two accounts,
    where one account (the sponsor/owner) provides XRP for fees and/or reserves
    on behalf of another account (the sponsee).
    """

    ledger_entry_type: LedgerEntryType = LedgerEntryType.SPONSORSHIP
    """The type of ledger entry. Always 'Sponsorship' for this entry type."""

    owner: str = REQUIRED  # type: ignore
    """
    The sponsor associated with this relationship.
    This account also pays for the reserve of this object.
    """

    sponsee: str = REQUIRED  # type: ignore
    """The sponsee associated with this relationship."""

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the sponsor's owner directory links to this object,
    in case the directory consists of multiple pages.
    """

    sponsee_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the sponsee's owner directory links to this object,
    in case the directory consists of multiple pages.
    """

    flags: int = 0
    """A bit-map of boolean flags enabled for this object."""

    fee_amount: Optional[str] = None
    """
    The (remaining) amount of XRP that the sponsor has provided for the sponsee
    to use for fees, in drops.
    """

    max_fee: Optional[str] = None
    """
    The maximum fee per transaction that will be sponsored, in drops.
    This prevents abuse/excessive draining of the sponsored fee pool.
    """

    reserve_count: int = 0
    """
    The (remaining) number of OwnerCount that the sponsor has provided
    for the sponsee to use for reserves.
    """

    previous_txn_id: Optional[str] = None
    """The identifying hash of the transaction that most recently modified this entry."""

    previous_txn_lgr_seq: Optional[int] = None
    """The ledger index that contains the transaction that most recently modified this object."""

    index: Optional[str] = None
    """The unique identifier for this ledger entry."""

    def _get_errors(self: Self) -> Dict[str, str]:
        """
        Validate the Sponsorship ledger entry.

        Returns:
            A dictionary of field names to error messages.
        """
        errors = super()._get_errors()

        # Owner and Sponsee must be different
        if self.owner == self.sponsee:
            errors["owner_sponsee"] = (
                "Owner and Sponsee must be different accounts. "
                "An account cannot sponsor itself."
            )

        # At least one of FeeAmount or ReserveCount must be provided
        if self.fee_amount is None and self.reserve_count == 0:
            errors["sponsorship_content"] = (
                "At least one of fee_amount or reserve_count must be provided."
            )

        # FeeAmount must be non-negative if provided
        if self.fee_amount is not None:
            try:
                fee_value = int(self.fee_amount)
                if fee_value < 0:
                    errors["fee_amount"] = "fee_amount must be non-negative."
            except ValueError:
                errors["fee_amount"] = "fee_amount must be a valid numeric string."

        # ReserveCount must be non-negative
        if self.reserve_count < 0:
            errors["reserve_count"] = "reserve_count must be non-negative."

        # MaxFee must be non-negative if provided
        if self.max_fee is not None:
            try:
                max_fee_value = int(self.max_fee)
                if max_fee_value < 0:
                    errors["max_fee"] = "max_fee must be non-negative."
            except ValueError:
                errors["max_fee"] = "max_fee must be a valid numeric string."

        return errors

