"""
The ledger_closed method returns the unique
identifiers of the most recently closed ledger.
(This ledger is not necessarily validated and
immutable yet.)
"""
from dataclasses import dataclass, field

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
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

    method: RequestMethod = field(default=RequestMethod.LEDGER_CLOSED, init=False)
    ledger_hash: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    ledger_index: int = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """
