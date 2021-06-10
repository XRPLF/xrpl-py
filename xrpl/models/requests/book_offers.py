"""
The book_offers method retrieves a list of offers, also known
as the order book, between two currencies.
"""
from dataclasses import dataclass, field
from typing import Optional, Union

from xrpl.models.currencies import Currency
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class BookOffers(Request):
    """
    The book_offers method retrieves a list of offers, also known
    as the order book, between two currencies.
    """

    taker_gets: Currency = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    taker_pays: Currency = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    method: RequestMethod = field(default=RequestMethod.BOOK_OFFERS, init=False)
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    limit: Optional[int] = None
    taker: Optional[str] = None
