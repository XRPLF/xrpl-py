"""Model for AccountLines request type."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from xrpl.models.requests.request import RequestMethod
from xrpl.models.utils import REQUIRED
from xrpl.models.requests.base_request import BaseRequest
from xrpl.models.requests.lookup_by_ledger import LookupByLedgerRequest
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AccountLines(BaseRequest, LookupByLedgerRequest):
    """
    The account_lines command retrieves information about an account's trust lines,
    including balances in all non-XRP currencies and assets. All information retrieved is
    relative to a particular version of the ledger. Returns an AccountLinesResponse
    """

    method: RequestMethod = field(default=RequestMethod.ACCOUNT_LINES, init=False)

    account: str = REQUIRED
    """
    The account to look up trust lines for.
    """

    peer: Optional[str] = None
    """
    (Optional) A second account; if provided, filter results to trust lines connecting the
    two accounts.
    """

    limit: Optional[int] = None
    """
    (Optional) Limit the number of trust lines to retrieve. Must be within the inclusive
    range 10 to 400. Default is 200.
    """

    marker: Optional[Dict[str, Any]] = None
    """
    (Optional) Value from a previous paginated response. Resume retrieving data where that
    response left off.
    """


