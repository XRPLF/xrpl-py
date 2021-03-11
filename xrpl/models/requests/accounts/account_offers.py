"""
This request retrieves a list of offers made by a given account that are
outstanding as of a particular ledger version.

`See account_offers <https://xrpl.org/account_offers.html>`_
"""
from dataclasses import dataclass
from typing import Any, Optional, Union

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class AccountOffers(Request):
    """
    This request retrieves a list of offers made by a given account that are
    outstanding as of a particular ledger version.

    `See account_offers <https://xrpl.org/account_offers.html>`_
    """

    account: str = REQUIRED  # type: ignore
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = RequestMethod.ACCOUNT_OFFERS
    limit: Optional[int] = None
    marker: Optional[Any] = None
    strict: Optional[bool] = False
