"""
The ledger_closed method returns the unique
identifiers of the most recently closed ledger.
(This ledger is not necessarily validated and
immutable yet.)
"""
from dataclasses import dataclass

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerClosed(Request):
    """
    The ledger_closed method returns the unique
    identifiers of the most recently closed ledger.
    (This ledger is not necessarily validated and
    immutable yet.)
    """

    method: RequestMethod = RequestMethod.LEDGER_CLOSED
    ledger_hash: str = REQUIRED
    ledger_index: int = REQUIRED
