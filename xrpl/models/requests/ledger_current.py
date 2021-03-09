"""
The ledger_current method returns the unique
identifiers of the current in-progress ledger.
This command is mostly useful for testing,
because the ledger returned is still in flux.
"""
from dataclasses import dataclass

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerCurrent(Request):
    """
    The ledger_current method returns the unique
    identifiers of the current in-progress ledger.
    This command is mostly useful for testing,
    because the ledger returned is still in flux.
    """

    method: RequestMethod = RequestMethod.LEDGER_CURRENT
