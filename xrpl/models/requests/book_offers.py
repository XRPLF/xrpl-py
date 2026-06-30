"""
The book_offers method retrieves a list of offers, also known
as the order book, between two currencies.
"""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.currencies import Currency
from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class BookOffers(Request, LookupByLedgerRequest):
    """
    The book_offers method retrieves a list of offers, also known
    as the order book, between two currencies.
    """

    taker_gets: Currency = REQUIRED
    """
    This field is required.

    :meta hide-value:
    """

    taker_pays: Currency = REQUIRED
    """
    This field is required.

    :meta hide-value:
    """

    method: RequestMethod = field(default=RequestMethod.BOOK_OFFERS, init=False)
    limit: Optional[int] = None
    taker: Optional[str] = None
    domain: Optional[str] = None
