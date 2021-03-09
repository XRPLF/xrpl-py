"""
This request retrieves a list of currencies that an account can send or receive,
based on its trust lines.

This is not a thoroughly confirmed list, but it can be used to populate user
interfaces.

`See account_currencies <https://xrpl.org/account_currencies.html>`_
"""
from dataclasses import dataclass
from typing import Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True)
class AccountCurrencies(Request):
    """
    This request retrieves a list of currencies that an account can send or receive,
    based on its trust lines.

    This is not a thoroughly confirmed list, but it can be used to populate user
    interfaces.

    `See account_currencies <https://xrpl.org/account_currencies.html>`_
    """

    account: str = REQUIRED
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = RequestMethod.ACCOUNT_CURRENCIES
    strict: Optional[bool] = False
