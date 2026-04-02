"""This method retrieves all of the NFTs currently owned by the specified account."""

from dataclasses import dataclass, field
from typing import Any, Optional

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class AccountNFTs(Request, LookupByLedgerRequest):
    """
    This method retrieves all of the NFTs currently owned
    by the specified account.
    """

    method: RequestMethod = field(default=RequestMethod.ACCOUNT_NFTS, init=False)
    account: str = REQUIRED
    """
    The unique identifier of an account, typically the account's address. The
    request returns NFTs owned by this account. This value is required.

    :meta hide-value:
    """

    limit: Optional[int] = None
    """Limit the number of NFTokens to retrieve."""

    # marker data shape is actually undefined in the spec, up to the
    # implementation of an individual server
    marker: Optional[Any] = None
    """
    Value from a previous paginated response. Resume retrieving data where
    that response left off.
    """
