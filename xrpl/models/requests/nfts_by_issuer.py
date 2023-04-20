"""
The `nfts_by_issuer` method retrieves all of the NFTokens
issued by an account
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTsByIssuer(Request):
    """
    The `nfts_by_issuer` method retrieves all of the NFTokens
    issued by an account
    """

    method: RequestMethod = field(default=RequestMethod.NFTS_BY_ISSUER, init=False)
    issuer: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    marker: Optional[Any] = None
    nft_taxon: Optional[int] = None
    limit: Optional[int] = None
