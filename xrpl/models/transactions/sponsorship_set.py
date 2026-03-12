"""Model for SponsorshipSet transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


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


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
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

    reserve_count: Optional[int] = None
    """The number of reserves to sponsor."""

    transaction_type: TransactionType = field(
        default=TransactionType.SPONSORSHIP_SET,
        init=False,
    )
