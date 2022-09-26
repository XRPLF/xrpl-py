"""Models for the Ledger Object `RippleState`"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class RippleState(LedgerObject):
    """The model for the `RippleState` Ledger Object"""

    balance: IssuedCurrencyAmount = REQUIRED  # type: ignore
    flags: int = REQUIRED  # type: ignore
    low_limit: IssuedCurrencyAmount = REQUIRED  # type: ignore
    high_limit: IssuedCurrencyAmount = REQUIRED  # type: ignore
    previous_txn_id: str = REQUIRED  # type: ignore
    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    high_node: Optional[str] = None
    low_node: Optional[str] = None
    high_quality_in: Optional[int] = None
    high_quality_out: Optional[int] = None
    low_quality_in: Optional[int] = None
    low_quality_out: Optional[int] = None
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.RIPPLE_STATE,
        init=False,
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class MDRippleStateFields(LedgerObject):
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


class RippleStateFlag(Enum):
    """The flags for the `RippleState` Ledger Object"""

    LSF_LOW_RESERVE = 0x00010000
    LSF_HIGH_RESERVE = 0x00020000
    LSF_LOW_AUTH = 0x00040000
    LSF_HIGH_AUTH = 0x00080000
    LSF_LOW_NO_RIPPLE = 0x00100000
    LSF_HIGH_NO_RIPPLE = 0x00200000
    LSF_LOW_FREEZE = 0x00400000
    LSF_HIGH_FREEZE = 0x00800000
