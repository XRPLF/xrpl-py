"""Model for RippleStateEntry."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.ripple_state_entry_ripple_state import RippleStateEntryRippleState
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class RippleStateEntry(BaseModel):
    """
    Retrieve a RippleState entry, which tracks a (non-XRP) currency balance between two
    accounts.
    """

    ripple_state: Optional[RippleStateEntryRippleState] = None
