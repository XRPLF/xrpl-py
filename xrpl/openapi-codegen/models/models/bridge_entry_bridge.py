"""Model for BridgeEntryBridge."""
from dataclasses import dataclass
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import REQUIRED
from xrpl.models.issued_currency import IssuedCurrency
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class BridgeEntryBridge(BaseModel):
    issuing_chain_door: str = REQUIRED
    issuing_chain_issue: IssuedCurrency = REQUIRED
    locking_chain_door: str = REQUIRED
    locking_chain_issue: IssuedCurrency = REQUIRED

