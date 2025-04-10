"""Model for NFTPageEntry."""
from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class NFTPageEntry(BaseModel):
    """
    Return an NFT Page in its raw ledger format.
    """

    nft_page: Optional[str] = None

