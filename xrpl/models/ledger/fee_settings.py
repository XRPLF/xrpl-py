"""Models for the Ledger Object `FeeSettings`"""

from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.ledger.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class FeeSettings(LedgerObject):
    """The model for the `FeeSettings` Ledger Object"""

    base_fee: str = REQUIRED  # type: ignore
    # always 0
    flags: int = REQUIRED  # type: ignore
    reference_fee_units: int = REQUIRED  # type: ignore
    reserve_base: int = REQUIRED  # type: ignore
    reserve_increment: int = REQUIRED  # type: ignore
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.FEE_SETTINGS, init=False
    )
