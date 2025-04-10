"""Model for BridgeEntry."""
from dataclasses import dataclass
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import REQUIRED
from xrpl.models.bridge_entry_bridge import BridgeEntryBridge
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class BridgeEntry(BaseModel):
    """
    Retrieve a Bridge entry, which represents a single cross-chain bridge that connects the
    XRP Ledger with another blockchain.
    """

    bridge_account: str = REQUIRED
    """
    The account that submitted the XChainCreateBridge transaction on the blockchain.
    """

    bridge: BridgeEntryBridge = REQUIRED

