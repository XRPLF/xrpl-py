"""Model for LedgerEntryByID."""
from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerEntryByID(BaseModel):
    """
    Retrieve any type of ledger object by its unique ID.
    """

    index: Optional[str] = None
    """
    The ledger entry ID of a single entry to retrieve from the ledger, as a 64-character
    (256-bit) hexadecimal string.
    """


