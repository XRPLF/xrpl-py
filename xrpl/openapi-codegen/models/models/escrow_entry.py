"""Model for EscrowEntry."""
from dataclasses import dataclass
from typing import Optional, Union
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class EscrowEntry(BaseModel):
    """
    Retrieve an Escrow entry, which holds XRP until a specific time or condition is met.
    """

    escrow: Optional[Union[str, EscrowEntryEscrowOneOf]] = None

