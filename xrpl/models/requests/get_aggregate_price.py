"""
This module defines the GetAggregatePrice request API. It is used to fetch aggregate
statistics about the specified PriceOracles
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from xrpl.models.nested_model import NestedModel
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class GetAggregatePrice(Request):
    """This request returns aggregate stats pertaining to the specified input oracles"""

    method: RequestMethod = field(default=RequestMethod.GET_AGGREGATE_PRICE, init=False)

    """base_asset is the asset to be priced"""
    base_asset: str = REQUIRED  # type: ignore

    """quote_asset is the denomination in which the prices are expressed"""
    quote_asset: str = REQUIRED  # type: ignore

    oracles: List[OracleInfo] = REQUIRED  # type: ignore

    """percentage of outliers to trim"""
    trim: Optional[int] = None

    """time_threshold : defines a range of prices to include based on the timestamp
    range - {most recent, most recent - time_threshold}"""
    time_threshold: Optional[int] = None

    def _get_errors(self: GetAggregatePrice) -> Dict[str, str]:
        errors = super()._get_errors()
        if len(self.oracles) == 0:
            errors[
                "GetAggregatePrice"
            ] = "Oracles array must contain at least one element"
        return errors


@require_kwargs_on_init
@dataclass(frozen=True)
class OracleInfo(NestedModel):
    """Represents one PriceData element. It is used in OracleSet transaction"""

    oracle_document_id: int = REQUIRED  # type: ignore
    account: str = REQUIRED  # type: ignore
