"""Model for TicketEntry."""
from dataclasses import dataclass
from typing import Optional, Union
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class TicketEntry(BaseModel):
    """
    Retrieve a Ticket entry, which represents a sequence number set aside for future use.
    """

    ticket: Optional[Union[str, TicketEntryTicketOneOf]] = None

