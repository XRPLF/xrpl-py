"""Models for the Metadata Object `SignerList`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.transactions.signer_list_set import SignerEntry
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SignerList(LedgerObject):
    """
    The model for the `SignerList` Ledger Object when
    represented in a transaction's metadata.
    """

    flags: Optional[int] = None
    owner_node: Optional[str] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    signer_entries: Optional[List[SignerEntry]] = None
    signer_list_id: Optional[int] = None
    signer_quorum: Optional[int] = None
