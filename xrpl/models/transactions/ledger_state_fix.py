"""Model for LedgerStateFix transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LedgerStateFix(Transaction):
    """Represents a LedgerStateFix transaction."""

    ledger_fix_type: int = REQUIRED  # type: ignore
    owner: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.LEDGER_STATE_FIX,
        init=False,
    )
