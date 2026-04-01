"""
The `nft_buy_offers` method retrieves all of buy offers
for the specified NFToken.
"""

from dataclasses import dataclass, field

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class NFTBuyOffers(Request, LookupByLedgerRequest):
    """
    The `nft_buy_offers` method retrieves all of buy offers
    for the specified NFToken.
    """

    method: RequestMethod = field(default=RequestMethod.NFT_BUY_OFFERS, init=False)
    nft_id: str = REQUIRED
    """
    The unique identifier of an NFToken.
    The request returns buy offers for this NFToken. This value is required.

    :meta hide-value:
    """
