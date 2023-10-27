"""Models for the Metadata Object `PayChannel`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class PayChannel(LedgerObject):
    """
    The model for the `PayChannel` Ledger Object when
    represented in a transaction's metadata.
    """

    account: Optional[str] = None
    amount: Optional[str] = None
    balance: Optional[str] = None
    destination: Optional[str] = None
    # always 0
    flags: Optional[int] = None
    owner_node: Optional[str] = None
    public_key: Optional[str] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    settle_delay: Optional[int] = None
    destination_node: Optional[str] = None
    destination_tag: Optional[int] = None
    expiration: Optional[int] = None
    cancel_after: Optional[int] = None
    source_tag: Optional[int] = None
