"""Models for the Ledger Object `NFTokenPage`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.nftoken_offer import NFToken
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenPage(LedgerObject):
    """The model for the `NFTokenPage` Ledger Object"""

    previous_page_min: Optional[str] = None
    next_page_min: Optional[str] = None
    previous_token_page: Optional[str] = None
    previous_token_next: Optional[str] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    nftokens: Optional[List[NFToken]] = None
    flags: int = 0
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.NFTOKEN_PAGE,
        init=False,
    )
