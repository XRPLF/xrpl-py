"""
This request returns information about an account's trust lines, including balances
in all non-XRP currencies and assets. All information retrieved is relative to a
particular version of the ledger.

`See account_lines <https://xrpl.org/account_lines.html>`_
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Union

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class AccountLines(Request):
    """
    This request returns information about an account's trust lines, including balances
    in all non-XRP currencies and assets. All information retrieved is relative to a
    particular version of the ledger.

    `See account_lines <https://xrpl.org/account_lines.html>`_
    """

    account: str = REQUIRED
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = field(default=RequestMethod.ACCOUNT_LINES, init=False)
    peer: Optional[str] = None
    limit: Optional[int] = None
    marker: Optional[Any] = None
