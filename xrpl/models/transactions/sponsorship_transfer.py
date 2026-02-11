"""Model for SponsorshipTransfer transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class SponsorshipTransfer(Transaction):
    """
    Represents a SponsorshipTransfer transaction, which transfers a sponsor relationship
    for a particular ledger object's reserve.

    The sponsor relationship can either be passed on to a new sponsor, or dissolved
    entirely (with the sponsee taking on the reserve). Either the sponsor or sponsee
    may submit this transaction at any point in time.

    There are three valid transfer scenarios:
    1. Transferring from sponsor to sponsee (sponsored to unsponsored)
    2. Transferring from sponsee to sponsor (unsponsored to sponsored)
    3. Transferring from sponsor to new sponsor
    """

    object_id: Optional[str] = None
    """
    The ID of the object to transfer sponsorship. If not included, this transaction
    refers to the account sending the transaction.
    """

    sponsor: Optional[str] = None
    """
    The new sponsor of the object. If included with tfSponsorReserve flag, the reserve
    sponsorship for the provided object will be transferred to this Sponsor. If omitted
    or if tfSponsorReserve flag is not included, the burden of the reserve will be
    passed back to the ledger object's owner (the former sponsee).
    """

    sponsor_flags: Optional[int] = None
    """
    Flags on the sponsorship, indicating what type of sponsorship this is
    (fee vs. reserve). Uses tfSponsorFee (0x00000001) and tfSponsorReserve (0x00000002).
    """

    sponsor_signature: Optional[SponsorSignature] = None
    """
    This field contains all the signing information for the sponsorship happening in
    the transaction. It is included if the transaction is fee- and/or reserve-sponsored.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.SPONSORSHIP_TRANSFER,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        """
        Validate the SponsorshipTransfer transaction.

        Returns:
            A dictionary of field names to error messages.
        """
        errors = super()._get_errors()

        # Validate sponsor_flags and sponsor_signature consistency
        # If sponsor field is present, sponsor_flags and sponsor_signature should be present
        if self.sponsor is not None:
            if self.sponsor_flags is None:
                errors["sponsor_flags"] = (
                    "SponsorFlags must be included when Sponsor field is present."
                )
            if self.sponsor_signature is None:
                errors["sponsor_signature"] = (
                    "SponsorSignature must be included when Sponsor field is present."
                )

        # If sponsor_flags is present, sponsor should be present
        if self.sponsor_flags is not None and self.sponsor is None:
            errors["sponsor"] = (
                "Sponsor field must be included when SponsorFlags is present."
            )

        # If sponsor_signature is present, sponsor should be present
        if self.sponsor_signature is not None and self.sponsor is None:
            errors["sponsor_for_signature"] = (
                "Sponsor field must be included when SponsorSignature is present."
            )

        # Validate sponsor_flags values (only tfSponsorFee and tfSponsorReserve are valid)
        if self.sponsor_flags is not None:
            TF_SPONSOR_FEE = 0x00000001
            TF_SPONSOR_RESERVE = 0x00000002
            valid_flags = TF_SPONSOR_FEE | TF_SPONSOR_RESERVE

            if self.sponsor_flags & ~valid_flags:
                errors["sponsor_flags_invalid"] = (
                    "SponsorFlags contains invalid flags. "
                    "Only tfSponsorFee (0x00000001) and tfSponsorReserve (0x00000002) "
                    "are valid."
                )

        return errors

