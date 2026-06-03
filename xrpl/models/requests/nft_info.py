"""
The `nft_info` method retrieves all the information about the
NFToken
"""

from dataclasses import dataclass, field

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class NFTInfo(Request, LookupByLedgerRequest):
    """
    The `nft_info` method retrieves all the information about the
    NFToken
    """

    method: RequestMethod = field(default=RequestMethod.NFT_INFO, init=False)
    nft_id: str = REQUIRED
    """
    The unique identifier of an NFToken.
    The request returns information of this NFToken. This value is required.

    :meta hide-value:
    """
