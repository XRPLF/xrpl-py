"""
This request returns information about all Sponsorship objects where the specified
account is the sponsor. This shows which accounts and objects the account is currently
sponsoring.

See XLS-0068 Sponsored Fees and Reserves for details.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class AccountSponsoring(Request, LookupByLedgerRequest):
    """
    This request returns information about all Sponsorship objects where the specified
    account is the sponsor. This shows which accounts and objects the account is
    currently sponsoring.

    See XLS-0068 Sponsored Fees and Reserves for details.
    """

    account: str = REQUIRED
    """
    The account to query for sponsorships. This field is required.

    :meta hide-value:
    """

    method: RequestMethod = field(
        default=RequestMethod.ACCOUNT_SPONSORING, init=False
    )
    limit: Optional[int] = None
    """
    Maximum number of Sponsorship objects to return. Server may return fewer.
    """

    # marker data shape is actually undefined in the spec, up to the
    # implementation of an individual server
    marker: Optional[Any] = None
    """
    Value from a previous paginated response. Resume retrieving data where that
    response left off.
    """

