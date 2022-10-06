"""Model for the Ledger Header"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from xrpl.models import LedgerEntryType, Metadata
from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Ledger(BaseModel):
    """The model for the Ledger Header"""

    account_hash: str = REQUIRED  # type: ignore
    close_flags: int = REQUIRED  # type: ignore
    close_time: int = REQUIRED  # type: ignore
    close_time_human: str = REQUIRED  # type: ignore
    close_time_resolution: int = REQUIRED  # type: ignore
    closed: bool = REQUIRED  # type: ignore
    ledger_hash: str = REQUIRED  # type: ignore
    ledger_index: str = REQUIRED  # type: ignore
    parent_close_time: int = REQUIRED  # type: ignore
    parent_hash: str = REQUIRED  # type: ignore
    total_coins: str = REQUIRED  # type: ignore
    transaction_hash: str = REQUIRED  # type: ignore
    account_state: Optional[List[LedgerEntryType]] = None
    transactions: Optional[List[Metadata]] = None
