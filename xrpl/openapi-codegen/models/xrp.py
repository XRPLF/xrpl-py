"""Model for XRP."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XRP(BaseModel):
    currency: Optional[str] = "XRP"
    """
    ^ Specifies XRP as a currency, without a value. Normally, you will not use this model as
    it does not specify an amount of XRP. In cases where you need to specify an amount of
    XRP, you will use a string. However, for some book order requests where currencies are
    specified without amounts, you may need to specify the use of XRP, without a value. In
    these cases, you will use this object.
    """
