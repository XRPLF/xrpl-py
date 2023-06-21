"""
The `nft_sell_offers` method retrieves all of sell offers
for the specified NFToken.
"""
from dataclasses import dataclass, field

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTSellOffers(Request, LookupByLedgerRequest):
    """
    The `nft_sell_offers` method retrieves all of sell offers
    for the specified NFToken.
    """

    method: RequestMethod = field(default=RequestMethod.NFT_SELL_OFFERS, init=False)
    nft_id: str = REQUIRED  # type: ignore
    """
    The unique identifier of an NFToken.
    The request returns sell offers for this NFToken. This value is required.

    :meta hide-value:
    """
