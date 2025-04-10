"""Model for AMMEntry."""
from dataclasses import dataclass
from typing import Optional, Union
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AMMEntry(BaseModel):
    """
    Retrieve an Automated Market-Maker (AMM) object from the ledger. This is similar to
    amm_info method, but the ledger_entry version returns only the ledger entry as stored.
    """

    amm: Optional[Union[str, AMMEntryAmmOneOf]] = None

