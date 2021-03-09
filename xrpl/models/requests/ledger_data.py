"""
The ledger_data method retrieves contents of
the specified ledger. You can iterate through
several calls to retrieve the entire contents
of a single ledger version.
"""
from dataclasses import dataclass
from typing import Any, Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerData(Request):
    """
    The ledger_data method retrieves contents of
    the specified ledger. You can iterate through
    several calls to retrieve the entire contents
    of a single ledger version.
    """

    method: RequestMethod = RequestMethod.LEDGER_DATA
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    binary: Optional[bool] = False
    limit: Optional[int] = None
    # TODO make type
    marker: Optional[Any] = None
