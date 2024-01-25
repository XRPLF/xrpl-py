"""Models for the Ledger Object `Offer`"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Offer(LedgerObject):
    """The model for the `Offer` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    """
    The address of the account that owns this Offer. This field is required.
    """

    book_directory: str = REQUIRED  # type: ignore
    """
    The ID of the Offer Directory that links to this Offer. This field is required.
    """

    book_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the offer directory links to this entry, in case
    the directory consists of multiple pages. This field is required.
    """

    expiration: Optional[int] = None
    """
    Indicates the time after which this Offer is considered unfunded. See Specifying
    Time for details.
    """

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the owner directory links to this entry, in case
    the directory consists of multiple pages. This field is required.
    """

    previous_txn_id: str = REQUIRED  # type: ignore
    """
    The identifying hash of the transaction that most recently modified this entry.
    This field is required.
    """

    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    """
    The index of the ledger that contains the transaction that most recently modified
    this object. This field is required.
    """

    sequence: int = REQUIRED  # type: ignore
    """
    The `Sequence` value of the `OfferCreate` transaction that created this offer. Used
    in combination with the `Account` to identify this offer. This field is required.
    """

    taker_gets: Union[str, IssuedCurrencyAmount] = REQUIRED  # type: ignore
    """
    The remaining amount and type of currency being provided by the `Offer` creator.
    This field is required.
    """

    taker_pays: Union[str, IssuedCurrencyAmount] = REQUIRED  # type: ignore
    """
    The remaining amount and type of currency requested by the `Offer` creator.
    This field is required.
    """

    flags: int = REQUIRED  # type: ignore
    """
    A bit-map of boolean flags.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.OFFER,
        init=False,
    )
    """
    The value 0x0050, mapped to the string NFTokenPage, indicates that this is a page
    containing NFToken objects.
    """


class OfferFlag(Enum):
    """The flags for the `Offer` Ledger Object"""

    LSF_PASSIVE = 0x00010000
    LSF_SELL = 0x00020000
