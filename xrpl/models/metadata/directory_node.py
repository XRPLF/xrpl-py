"""Models for the Metadata Object `DirectoryNode`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DirectoryNode(LedgerObject):
    """
    The model for the `DirectoryNode` Ledger Object when
    represented in a transaction's metadata.
    """

    # always 0
    flags: Optional[int] = None
    root_index: Optional[str] = None
    indexes: Optional[List[str]] = None
    index_next: Optional[int] = None
    index_previous: Optional[int] = None
    owner: Optional[str] = None
    exchange_rate: Optional[str] = None
    taker_pays_currency: Optional[str] = None
    taker_pays_issuer: Optional[str] = None
    taker_gets_currency: Optional[str] = None
    taker_gets_issuer: Optional[str] = None
