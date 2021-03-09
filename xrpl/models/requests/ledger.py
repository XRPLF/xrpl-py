"""Retrieve information about the public ledger."""
from dataclasses import dataclass
from typing import Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Ledger(Request):
    """Retrieve information about the public ledger."""

    method: RequestMethod = RequestMethod.LEDGER
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    full: Optional[bool] = None
    accounts: Optional[bool] = False
    transactions: Optional[bool] = False
    expand: Optional[bool] = False
    owner_funds: Optional[bool] = False
    binary: Optional[bool] = None
    queue: Optional[bool] = None
