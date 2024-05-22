"""
The `nfts_by_issuer` method retrieves all of the NFTokens
issued by an account
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Union

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTsByIssuer(Request, LookupByLedgerRequest):
    """
    The `nfts_by_issuer` method retrieves all of the NFTokens
    issued by an account
    """

    method: RequestMethod = field(default=RequestMethod.NFTS_BY_ISSUER, init=False)
    issuer: str = REQUIRED  # type: ignore

    marker: Optional[Any] = None
    nft_taxon: Optional[int] = None
    limit: Optional[int] = None
