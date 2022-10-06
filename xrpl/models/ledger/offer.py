"""Models for the Ledger Object `Offer`"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Offer(LedgerObject):
    """The model for the `Offer` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    taker_gets: Union[str, IssuedCurrencyAmount] = REQUIRED  # type: ignore
    taker_pays: Union[str, IssuedCurrencyAmount] = REQUIRED  # type: ignore
    sequence: int = REQUIRED  # type: ignore
    flags: int = REQUIRED  # type: ignore
    book_directory: str = REQUIRED  # type: ignore
    book_node: str = REQUIRED  # type: ignore
    owner_node: str = REQUIRED  # type: ignore
    previous_txn_id: str = REQUIRED  # type: ignore
    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    expiration: Optional[int] = None
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.OFFER,
        init=False,
    )


class OfferFlag(Enum):
    """The flags for the `Offer` Ledger Object"""

    LSF_PASSIVE = 0x00010000
    LSF_SELL = 0x00020000
