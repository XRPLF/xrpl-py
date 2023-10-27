"""Models for the Metadata Object `Amendments`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from xrpl.models.ledger_objects import Majority
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Amendments(LedgerObject):
    """
    The model for the `Amendments` Ledger Object when
    represented in a transaction's metadata.
    """

    # always 0
    flags: Optional[int] = None
    amendments: Optional[List[str]] = None
    majorities: Optional[List[Majority]] = None
