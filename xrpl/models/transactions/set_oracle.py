"""Model for OracleSet transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OracleSet(Transaction):
    """Represents a OracleSet transaction."""

    account: str = REQUIRED  # type: ignore
    oracle_document_id: int = REQUIRED  # type: ignore

    """
    The below three fields must be hex-encoded. You can
    use `xrpl.utils.str_to_hex` to convert a UTF-8 string to hex.
    """
    provider: Optional[str] = None
    uri: Optional[str] = None
    asset_class: Optional[str] = None

    last_update_time: int = REQUIRED  # type: ignore
    price_data_series: List[PriceData] = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.SET_ORACLE,
        init=False,
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class PriceData(NestedModel):
    """Represents one PriceData element. It is used in OracleSet transaction"""

    base_asset: str = REQUIRED  # type: ignore
    quote_asset: str = REQUIRED  # type: ignore
    asset_price: Optional[int] = None
    scale: Optional[int] = None
