"""Models for the Metadata Object `Offer`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Offer(LedgerObject):
    """
    The model for the `Offer` Ledger Object when
    represented in a transaction's metadata.
    """

    account: Optional[str] = None
    taker_gets: Optional[Union[str, IssuedCurrencyAmount]] = None
    taker_pays: Optional[Union[str, IssuedCurrencyAmount]] = None
    sequence: Optional[int] = None
    flags: Optional[int] = None
    book_directory: Optional[str] = None
    book_node: Optional[str] = None
    owner_node: Optional[str] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    expiration: Optional[int] = None
