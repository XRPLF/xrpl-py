"""Model for CheckEntry."""
from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class CheckEntry(BaseModel):
    """
    Retrieve a Check entry, which is a potential payment that can be cashed by its
    recipient.
    """

    check: Optional[str] = None

