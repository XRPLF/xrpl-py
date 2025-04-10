"""Model for PriceData."""
from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import REQUIRED
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class PriceData(BaseModel):
    base_asset: str = REQUIRED
    """
    The primary asset in a trading pair (e.g., BTC in BTC/USD). Any valid identifier, such
    as a stock symbol, bond CUSIP, or currency code, is allowed.
    """

    quote_asset: str = REQUIRED
    """
    The quote asset in a trading pair, denoting the price of one unit of the base asset
    (e.g., USD in BTC/USD).
    """

    asset_price: Optional[str] = None
    """
    The asset price after applying the Scale precision level.  Recommended to be provided as
    a hexadecimal, but decimal numbers are accepted. Not included if the last update
    transaction didn't include the BaseAsset/QuoteAsset pair.
    """

    scale: Optional[int] = None
    """
    The scaling factor to apply to an asset price. If Scale is 6 and the original price is
    0.155,  then the scaled price is 155000. Valid scale ranges are 0-10. Not included if
    the last update transaction didn't include the BaseAsset/QuoteAsset pair.
    """

    def _get_errors(self: PriceData) -> Dict[str, str]:
        errors = super._get_errors()
        if (self.asset_price is not None) != (self.scale is not None):
            errors["PriceData"] = "Both `asset_price` and `scale` are required if any is presented."
        if (
            self.asset_price is not None 
            and self.asset_price != REQUIRED
            and not self.asset_price.isnumeric()
        ):
            errors["PriceData"] = "`asset_price` must be numeric."
        if self.scale is not None and self.scale < 0:
            errors["PriceData"] = "Field `scale` must have a value greater than or equal to 0"
        if self.scale is not None and self.scale > 10:
            errors["PriceData"] = "Field `scale` must have a value less than or equal to 10"
        return errors


