"""Model for OracleSet transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init

MAX_ORACLE_DATA_SERIES = 10
MAX_ORACLE_PROVIDER = 256
MAX_ORACLE_URI = 256
MAX_ORACLE_SYMBOL_CLASS = 16


@require_kwargs_on_init
@dataclass(frozen=True)
class OracleSet(Transaction):
    """Represents a OracleSet transaction."""

    account: str = REQUIRED  # type: ignore
    """Account is the XRPL account that has update and delete privileges on the Oracle
    being set. This field corresponds to the Owner field on the PriceOracle ledger
    object."""

    oracle_document_id: int = REQUIRED  # type: ignore
    """OracleDocumentID is a unique identifier of the Price Oracle for the given
    Account."""

    provider: Optional[str] = None
    """
    This field must be hex-encoded. You can use `xrpl.utils.str_to_hex` to
    convert a UTF-8 string to hex.
    """

    uri: Optional[str] = None
    """
    This field must be hex-encoded. You can use `xrpl.utils.str_to_hex` to
    convert a UTF-8 string to hex.
    """

    asset_class: Optional[str] = None
    """
    This field must be hex-encoded. You can use `xrpl.utils.str_to_hex` to
    convert a UTF-8 string to hex.
    """

    last_update_time: int = REQUIRED  # type: ignore
    """LastUpdateTime is the specific point in time when the data was last updated.
    The LastUpdateTime is represented as Unix Time - the number of seconds since
    January 1, 1970 (00:00 UTC)."""

    price_data_series: List[PriceData] = REQUIRED  # type: ignore
    """PriceDataSeries is an array of up to ten PriceData objects, where PriceData
    represents the price information for a token pair"""

    transaction_type: TransactionType = field(
        default=TransactionType.ORACLE_SET,
        init=False,
    )

    def _get_errors(self: OracleSet) -> Dict[str, str]:
        errors = super()._get_errors()

        # If price_data_series is not set, do not perform further validation
        if "price_data_series" not in errors and (
            len(self.price_data_series) == 0
            or len(self.price_data_series) > MAX_ORACLE_DATA_SERIES
        ):
            errors["OracleSet: price_data_series"] = (
                "The Price Data Series list must have a length of >0 and <"
                + str(MAX_ORACLE_DATA_SERIES)
                + "."
            )

        if self.asset_class and (
            len(self.asset_class) == 0
            or len(self.asset_class) > MAX_ORACLE_SYMBOL_CLASS
        ):
            errors["OracleSet: asset_class"] = (
                "The asset_class field must have a length of >0 and <"
                + str(MAX_ORACLE_SYMBOL_CLASS)
                + "."
            )

        if self.provider and (
            len(self.provider) == 0 or len(self.provider) > MAX_ORACLE_PROVIDER
        ):
            errors["OracleSet: provider"] = (
                "The provider field must have a length of >0 and <"
                + str(MAX_ORACLE_PROVIDER)
                + "."
            )

        if self.uri and (len(self.uri) == 0 or len(self.uri) > MAX_ORACLE_URI):
            errors["OracleSet: uri"] = (
                "The uri field must have a length of >0 and <"
                + str(MAX_ORACLE_URI)
                + "."
            )

        return errors


@require_kwargs_on_init
@dataclass(frozen=True)
class PriceData(NestedModel):
    """Represents one PriceData element. It is used in OracleSet transaction"""

    base_asset: str = REQUIRED  # type: ignore
    """BaseAsset refers to the primary asset within a trading pair. It is the asset
    against which the price of the quote asset is quoted."""

    quote_asset: str = REQUIRED  # type: ignore
    """QuoteAsset represents the secondary or quote asset in a trading pair. It denotes
    the price of one unit of the base asset."""

    asset_price: Optional[int] = None
    """AssetPrice is the scaled asset price, which is the price value after applying
    the scaling factor."""

    scale: Optional[int] = None
    """Scale is the price's scaling factor.
    It represents the price's precision level. """
