"""
This module defines the GetAggregatePrice request API. It is used to fetch aggregate
statistics about the specified PriceOracles
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import TypedDict

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class GetAggregatePrice(Request):
    """This request returns aggregate stats pertaining to the specified input oracles"""

    method: RequestMethod = field(default=RequestMethod.GET_AGGREGATE_PRICE, init=False)

    base_asset: str = REQUIRED  # type: ignore
    """base_asset is the asset to be priced"""

    quote_asset: str = REQUIRED  # type: ignore
    """quote_asset is the denomination in which the prices are expressed"""

    oracles: List[Oracle] = REQUIRED  # type: ignore
    """oracles is an array of oracle objects to aggregate over"""

    trim: Optional[int] = None
    """percentage of outliers to trim"""

    time_threshold: Optional[int] = None
    """time_threshold : defines a range of prices to include based on the timestamp
    range - {most recent, most recent - time_threshold}"""

    def _get_errors(self: GetAggregatePrice) -> Dict[str, str]:
        errors = super()._get_errors()
        if len(self.oracles) == 0:
            errors[
                "GetAggregatePrice"
            ] = "Oracles array must contain at least one element"
        return errors


@require_kwargs_on_init
@dataclass(frozen=True)
class Oracle(TypedDict):
    """Represents one Oracle element. It is used in GetAggregatePrice request"""

    oracle_document_id: int = REQUIRED  # type: ignore
    """oracle_document_id is a unique identifier of the Price Oracle for the given
    Account"""

    account: str = REQUIRED  # type: ignore
    """account is the Oracle's account."""
