"""Models for the Metadata Object `DepositPreauth`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DepositPreauth(LedgerObject):
    """
    The model for the `DepositPreauth` Ledger Object when
    represented in a transaction's metadata.
    """

    account: Optional[str] = None
    authorize: Optional[str] = None
    # always 0
    flags: Optional[int] = None
    owner_node: Optional[str] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
