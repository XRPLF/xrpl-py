"""
This request retrieves a list of currencies that an account can send or receive,
based on its trust lines.

This is not a thoroughly confirmed list, but it can be used to populate user
interfaces.

`See account_currencies <https://xrpl.org/account_currencies.html>`_
"""

from dataclasses import dataclass, field

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class AccountCurrencies(Request, LookupByLedgerRequest):
    """
    This request retrieves a list of currencies that an account can send or receive,
    based on its trust lines.

    This is not a thoroughly confirmed list, but it can be used to populate user
    interfaces.

    `See account_currencies <https://xrpl.org/account_currencies.html>`_
    """

    account: str = REQUIRED
    """
    This field is required.

    :meta hide-value:
    """
    method: RequestMethod = field(default=RequestMethod.ACCOUNT_CURRENCIES, init=False)
    strict: bool = False
