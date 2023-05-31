"""
The `nft_info` method retrieves all the information about the
NFToken
"""
from dataclasses import dataclass, field
from typing import Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTInfo(Request):
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

    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
