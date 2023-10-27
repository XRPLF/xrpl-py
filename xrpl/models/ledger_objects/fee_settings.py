"""Models for the Ledger Object `FeeSettings`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
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


@require_kwargs_on_init
@dataclass(frozen=True)
class MDFeeSettingsFields(LedgerObject):
    """
    The model for the `FeeSettings` Ledger Object when
    represented in a transaction's metadata.
    """

    base_fee: Optional[str] = None
    # always 0
    flags: Optional[int] = None
    reference_fee_units: Optional[int] = None
    reserve_base: Optional[int] = None
    reserve_increment: Optional[int] = None
