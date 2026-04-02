"""
The ledger_closed method returns the unique
identifiers of the most recently closed ledger.
(This ledger is not necessarily validated and
immutable yet.)
"""

from dataclasses import dataclass, field

from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True, kw_only=True)
class LedgerClosed(Request):
    """
    The ledger_closed method returns the unique
    identifiers of the most recently closed ledger.
    (This ledger is not necessarily validated and
    immutable yet.)
    """

    method: RequestMethod = field(default=RequestMethod.LEDGER_CLOSED, init=False)
