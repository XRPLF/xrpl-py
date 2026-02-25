"""
The `nfts_by_issuer` method retrieves all of the NFTokens
issued by an account
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class NFTsByIssuer(Request, LookupByLedgerRequest):
    """
    The `nfts_by_issuer` method retrieves all of the NFTokens
    issued by an account
    """

    method: RequestMethod = field(default=RequestMethod.NFTS_BY_ISSUER, init=False)
    issuer: str = REQUIRED
    """
    The unique identifier for an account that issues NFTokens
    The request returns NFTokens issued by this account. This field is required

    :meta hide-value:
    """

    marker: Optional[Any] = None
    nft_taxon: Optional[int] = None
    limit: Optional[int] = None
