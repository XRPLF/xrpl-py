"""
The ledger_current method returns the unique
identifiers of the current in-progress ledger.
This command is mostly useful for testing,
because the ledger returned is still in flux.
"""
from dataclasses import dataclass

from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class LedgerCurrent(Request):
    """
    The ledger_current method returns the unique
    identifiers of the current in-progress ledger.
    This command is mostly useful for testing,
    because the ledger returned is still in flux.
    """

    method: RequestMethod = RequestMethod.LEDGER_CURRENT
