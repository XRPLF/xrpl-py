"""Model for SponsorshipTransfer transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.transactions.transaction import (
    SponsorFlag,
    Transaction,
    TransactionFlagInterface,
)
from xrpl.models.transactions.types import TransactionType


class SponsorshipTransferFlag(int, Enum):
    """
    Enum for SponsorshipTransfer Transaction Flags.

    Transactions of the SponsorshipTransfer type support additional values in the
    Flags field. This enum represents those options.
    """

    TF_SPONSORSHIP_END = 0x00010000
    """End sponsorship of an object."""

    TF_SPONSORSHIP_CREATE = 0x00020000
    """Create sponsorship of an object."""

    TF_SPONSORSHIP_REASSIGN = 0x00040000
    """Reassign sponsorship of an object."""


class SponsorshipTransferFlagInterface(TransactionFlagInterface):
    """
    Transactions of the SponsorshipTransfer type support additional values in the
    Flags field. This TypedDict represents those options.
    """

    TF_SPONSORSHIP_END: bool
    TF_SPONSORSHIP_CREATE: bool
    TF_SPONSORSHIP_REASSIGN: bool


@dataclass(frozen=True, kw_only=True)
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

        # Exactly one of the three operation flags must be set.
        if sum([end, create, reassign]) != 1:
            errors["flags"] = (
                "Exactly one of `TF_SPONSORSHIP_END`, `TF_SPONSORSHIP_CREATE`, or "
                "`TF_SPONSORSHIP_REASSIGN` must be set."
            )

        # sponsee is only meaningful when ending sponsorship. The C++ preflight
        # rejects it for both CREATE and REASSIGN operations.
        if self.sponsee is not None and create:
            errors["sponsee"] = (
                "`sponsee` cannot be set when `TF_SPONSORSHIP_CREATE` is active."
            )
        elif self.sponsee is not None and reassign:
            errors["sponsee"] = (
                "`sponsee` cannot be set when `TF_SPONSORSHIP_REASSIGN` is active."
            )

        # Create and Reassign both name the incoming reserve sponsor, so they
        # need `sponsor` (temMALFORMED) carrying `spfSponsorReserve`
        # (temINVALID_FLAG).
        if create or reassign:
            operation = "TF_SPONSORSHIP_CREATE" if create else "TF_SPONSORSHIP_REASSIGN"
            if self.sponsor is None:
                errors["sponsor"] = (
                    f"`sponsor` is required when `{operation}` is active; it "
                    "names the sponsor taking on the reserve."
                )
            elif isinstance(self.sponsor_flags, int) and not (
                self.sponsor_flags & SponsorFlag.SPF_SPONSOR_RESERVE
            ):
                errors["sponsor_flags"] = (
                    f"`sponsor_flags` must include `SPF_SPONSOR_RESERVE` (0x2) "
                    f"when `{operation}` is active."
                )

        # Ending sponsorship removes a sponsor rather than naming one, so
        # `sponsor` must be absent (temMALFORMED). `sponsor_flags` without
        # `sponsor` is already rejected on the base transaction.
        if end:
            if self.sponsor is not None:
                errors["sponsor"] = (
                    "`sponsor` cannot be set when `TF_SPONSORSHIP_END` is active; "
                    "ending removes the existing sponsor rather than naming one."
                )
            if self.sponsee is not None and self.sponsee == self.account:
                errors["sponsee"] = (
                    "`sponsee` must differ from `account`; omit it to end the "
                    "submitter's own sponsorship."
                )

        # Not validated here: rippled also requires `SponsorSignature` on an
        # account-level Create/Reassign (one with no `object_id`). That check
        # cannot move to the model -- it runs at preflight, whereas models
        # validate at construction, and the transaction must be constructible
        # before anyone can sign it.

        return errors
