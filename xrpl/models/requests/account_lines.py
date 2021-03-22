"""
This request returns information about an account's trust lines, including balances
in all non-XRP currencies and assets. All information retrieved is relative to a
particular version of the ledger.

`See account_lines <https://xrpl.org/account_lines.html>`_
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountLines(Request):
    """
    This request returns information about an account's trust lines, including balances
    in all non-XRP currencies and assets. All information retrieved is relative to a
    particular version of the ledger.

    `See account_lines <https://xrpl.org/account_lines.html>`_
    """

    #: This field is required.
    account: str = REQUIRED  # type: ignore
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = field(default=RequestMethod.ACCOUNT_LINES, init=False)
    peer: Optional[str] = None
    limit: Optional[int] = None
    # marker data shape is actually undefined in the spec, up to the
    # implementation of an individual server
    marker: Optional[Any] = None
