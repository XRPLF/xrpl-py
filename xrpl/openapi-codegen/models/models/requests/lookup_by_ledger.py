"""Model for LookupByLedgerRequest."""
from dataclasses import dataclass
from typing import Optional, Union
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class LookupByLedgerRequest(BaseModel):
    """
    Additional information shared in requests which search for specific ledger data.
    """

    ledger_hash: Optional[str] = None
    """
    A 20-byte hex string for the ledger version to use.
    """

    ledger_index: Optional[Union[str, int]] = None

