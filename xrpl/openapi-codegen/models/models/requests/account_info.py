"""Model for AccountInfo request type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.requests.request import RequestMethod
from xrpl.models.utils import REQUIRED
from xrpl.models.requests.base_request import BaseRequest
from xrpl.models.requests.lookup_by_ledger import LookupByLedgerRequest
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountInfo(BaseRequest, LookupByLedgerRequest):
    """
    The account_info command retrieves information about an account, its activity, and its
    XRP balance. All information retrieved is relative to a particular version of the
    ledger. Returns an AccountInfoResponse
    """

    method: RequestMethod = field(default=RequestMethod.ACCOUNT_INFO, init=False)

    account: str = REQUIRED
    """
    The account to look up.
    """

    queue: Optional[bool] = None
    """
    If true, return stats about queued transactions sent by this account. Can only be used
    when querying for the data from the current open ledger. Not available from servers in
    Reporting Mode.
    """

    signer_lists: Optional[bool] = None
    """
    API v1: If true, return any SignerList objects associated with this account. API v2:
    Identical to v1, but also returns an invalidParams error if you provide a non-boolean
    value.
    """
