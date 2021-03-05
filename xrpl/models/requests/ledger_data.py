"""
The ledger_data method retrieves contents of
the specified ledger. You can iterate through
several calls to retrieve the entire contents
of a single ledger version.
"""
from dataclasses import dataclass
from typing import Any, Optional, Union

from xrpl.models.requests.request import Request, RequestMethod


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
    # marker data shape is actually undefined in the spec, up to the
    # implementation of an individual server
    marker: Optional[Any] = None
