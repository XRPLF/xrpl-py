"""Models for the Metadata Object `RippleState`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class RippleState(LedgerObject):
    """
    The model for the `RippleState` Ledger Object when
    represented in a transaction's metadata.
    """

    balance: Optional[IssuedCurrencyAmount] = None
    flags: Optional[int] = None
    low_limit: Optional[IssuedCurrencyAmount] = None
    high_limit: Optional[IssuedCurrencyAmount] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    high_node: Optional[str] = None
    low_node: Optional[str] = None
    high_quality_in: Optional[int] = None
    high_quality_out: Optional[int] = None
    low_quality_in: Optional[int] = None
    low_quality_out: Optional[int] = None
