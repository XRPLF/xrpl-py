"""Model for OracleSet transaction type."""

from dataclasses import dataclass, field
from typing import List, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.price_data import PriceData
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OracleSet(Transaction):
    transaction_type: TransactionType = field(
        default=TransactionType.ORACLE_SET, init=False
    )

    oracle_document_id: int = REQUIRED
    """
    A unique identifier of the price oracle for the Account.
    """

    provider: Optional[str] = None
    """
    An arbitrary value identifying an oracle provider, such as Chainlink, Band, or DIA. 
    This field is a string, up to 256 ASCII hex-encoded characters (0x20-0x7E). Required
    when creating a new Oracle ledger entry, but optional for updates.
    """

    uri: Optional[str] = None
    """
    An optional Universal Resource Identifier (URI) to reference price data off-chain. 
    Limited to 256 bytes.
    """

    last_update_time: int = REQUIRED
    """
    The timestamp indicating the last time the data was updated,  in seconds since the UNIX
    Epoch.
    """

    asset_class: Optional[str] = None
    """
    Describes the type of asset, such as \"currency\", \"commodity\", or \"index\".  This
    field is a string, up to 16 ASCII hex-encoded characters (0x20-0x7E). Required when
    creating a new Oracle ledger entry, but optional for updates.
    """

    price_data_series: List[PriceData] = REQUIRED
    """
    An array of up to 10 PriceData objects, each representing price information for a token
    pair.
    """

    def _get_errors(self: OracleSet) -> Dict[str, str]:
        errors = super._get_errors()
        if self.last_update_time is not None and self.last_update_time <= 946684799:
            errors["OracleSet"] = "last_update_time must be greater than 946684799"
        if self.provider is not None and len(self.provider) > 256:
            errors["OracleSet"] = (
                "Field `provider` must have a length less than or equal to 256"
            )
        if self.uri is not None and len(self.uri) > 256:
            errors["OracleSet"] = (
                "Field `uri` must have a length less than or equal to 256"
            )
        if self.asset_class is not None and len(self.asset_class) > 16:
            errors["OracleSet"] = (
                "Field `asset_class` must have a length less than or equal to 16"
            )
        if self.price_data_series is not None and len(self.price_data_series) < 1:
            errors["OracleSet"] = (
                "Field `price_data_series` must have a length greater than or equal to 1"
            )
        if self.price_data_series is not None and len(self.price_data_series) > 10:
            errors["OracleSet"] = (
                "Field `price_data_series` must have a length less than or equal to 10"
            )
        return errors
