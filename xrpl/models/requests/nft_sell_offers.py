"""
The `nft_sell_offers` method retrieves all of sell offers
for the specified NFToken.
"""

from dataclasses import dataclass, field

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class NFTSellOffers(Request, LookupByLedgerRequest):
    """
    The `nft_sell_offers` method retrieves all of sell offers
    for the specified NFToken.
    """

    method: RequestMethod = field(default=RequestMethod.NFT_SELL_OFFERS, init=False)
    nft_id: str = REQUIRED
    """
    The unique identifier of an NFToken.
    The request returns sell offers for this NFToken. This value is required.

    :meta hide-value:
    """
