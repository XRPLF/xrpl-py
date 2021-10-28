"""
The `nft_buy_offers` method retrieves all of buy offers
for the specified NFToken.
"""
from dataclasses import dataclass

from xrpl.models.requests.request import Request
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTBuyOffers(Request):
    """
    The `nft_buy_offers` method retrieves all of buy offers
    for the specified NFToken.
    """

    token_id: str = REQUIRED  # type: ignore
    """
    The unique identifier of an NFToken.
    The request returns buy offers for this NFToken.
    """
