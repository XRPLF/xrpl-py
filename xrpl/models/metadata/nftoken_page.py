"""Models for the Metadata Object `NFTokenPage`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.nftoken_offer import NFToken
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenPage(LedgerObject):
    """
    The model for the `NFTokenPage` Ledger Object when
    represented in a transaction's metadata.
    """

    previous_page_min: Optional[str] = None
    next_page_min: Optional[str] = None
    previous_token_page: Optional[str] = None
    previous_token_next: Optional[str] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    nftokens: Optional[List[NFToken]] = None
