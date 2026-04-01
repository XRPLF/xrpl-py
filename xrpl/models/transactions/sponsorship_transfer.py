"""Model for SponsorshipTransfer transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class SponsorshipTransferFlag(int, Enum):
    """
    Enum for SponsorshipTransfer Transaction Flags.

    Transactions of the SponsorshipTransfer type support additional values in the
    Flags field. This enum represents those options.
    """

    TF_SPONSORSHIP_END = 0x00000001
    """End sponsorship of an object."""

    TF_SPONSORSHIP_CREATE = 0x00000002
    """Create sponsorship of an object."""

    TF_SPONSORSHIP_REASSIGN = 0x00000004
    """Reassign sponsorship of an object."""


class SponsorshipTransferFlagInterface(TransactionFlagInterface):
    """
    Transactions of the SponsorshipTransfer type support additional values in the
    Flags field. This TypedDict represents those options.
    """

    TF_SPONSORSHIP_END: bool
    TF_SPONSORSHIP_CREATE: bool
    TF_SPONSORSHIP_REASSIGN: bool


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class SponsorshipTransfer(Transaction):
    """
    Represents a SponsorshipTransfer transaction, which transfers
    sponsorship of ledger objects on the XRP Ledger.
    """

    object_id: Optional[str] = None
    """The ID of the ledger object whose sponsorship is being transferred."""

    sponsee: Optional[str] = None
    """The account that is being sponsored."""

    transaction_type: TransactionType = field(
        default=TransactionType.SPONSORSHIP_TRANSFER,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        end = self.has_flag(int(SponsorshipTransferFlag.TF_SPONSORSHIP_END))
        create = self.has_flag(int(SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE))
        reassign = self.has_flag(int(SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN))

        # Exactly one of the three operation flags may be set at a time.
        if sum([end, create, reassign]) > 1:
            errors["flags"] = (
                "Exactly one of `TF_SPONSORSHIP_END`, `TF_SPONSORSHIP_CREATE`, or "
                "`TF_SPONSORSHIP_REASSIGN` may be set at a time."
            )

        # sponsee is not used for CREATE operation.
        if self.sponsee is not None and create:
            errors["sponsee"] = (
                "`sponsee` cannot be set when `TF_SPONSORSHIP_CREATE` is active."
            )

        return errors
