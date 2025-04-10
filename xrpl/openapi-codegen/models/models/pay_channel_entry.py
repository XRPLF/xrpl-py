"""Model for PayChannelEntry."""
from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class PayChannelEntry(BaseModel):
    """
    Retrieve a PayChannel entry, which holds XRP for asynchronous payments.
    """

    payment_channel: Optional[str] = None

