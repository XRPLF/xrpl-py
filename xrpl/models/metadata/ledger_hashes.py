"""Models for the Metadata Object `LedgerHashes`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerHashes(LedgerObject):
    """
    The model for the `LedgerHashes` Ledger Object when
    represented in a transaction's metadata.
    """

    first_ledger_sequence: Optional[int] = None
    last_ledger_sequence: Optional[int] = None
    hashes: Optional[List[str]] = None
    # always 0
    flags: Optional[int] = None
