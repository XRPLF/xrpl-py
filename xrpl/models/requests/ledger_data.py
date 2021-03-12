"""
The ledger_data method retrieves contents of
the specified ledger. You can iterate through
several calls to retrieve the entire contents
of a single ledger version.
`See ledger data <https://xrpl.org/ledger_data.html>`_
"""
from dataclasses import dataclass, field
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
    `See ledger data <https://xrpl.org/ledger_data.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.LEDGER_DATA, init=False)
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    binary: bool = False
    limit: Optional[int] = None
    # marker data shape is actually undefined in the spec, up to the
    # implementation of an individual server
    marker: Optional[Any] = None
