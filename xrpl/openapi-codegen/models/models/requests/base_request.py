"""Model for BaseRequest."""
from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class BaseRequest(BaseModel):
    """
    Information which could be included in every request sent to rippled
    """

    api_version: Optional[int] = None
    """
    The API version to use. If omitted, uses version 1.
    """


