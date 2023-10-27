"""Models for the Ledger Object `LedgerHashes`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerHashes(LedgerObject):
    """The model for the `LedgerHashes` Ledger Object"""

    first_ledger_sequence: int = REQUIRED  # type: ignore
    last_ledger_sequence: int = REQUIRED  # type: ignore
    hashes: List[str] = REQUIRED  # type: ignore
    # always 0
    flags: int = REQUIRED  # type: ignore
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.LEDGER_HASHES,
        init=False,
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class MDLedgerHashesFields(LedgerObject):
    """
    The model for the `LedgerHashes` Ledger Object when
    represented in a transaction's metadata.
    """

    first_ledger_sequence: Optional[int] = None
    last_ledger_sequence: Optional[int] = None
    hashes: Optional[List[str]] = None
    # always 0
    flags: Optional[int] = None
