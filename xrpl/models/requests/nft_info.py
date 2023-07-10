"""
The `nft_info` method retrieves all the information about the
NFToken
"""
from dataclasses import dataclass, field

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTInfo(Request, LookupByLedgerRequest):
    """
    The `nft_info` method retrieves all the information about the
    NFToken
    """

    method: RequestMethod = field(default=RequestMethod.NFT_INFO, init=False)
    nft_id: str = REQUIRED  # type: ignore
    """
    The unique identifier of an NFToken.
    The request returns information of this NFToken. This value is required.

    :meta hide-value:
    """
