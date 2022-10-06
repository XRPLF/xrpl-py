"""Models for the Ledger Object `Ticket`"""

from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.ledger.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Ticket(LedgerObject):
    """The model for the `Ticket` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    # always 0
    flags: int = REQUIRED  # type: ignore
    owner_node: str = REQUIRED  # type: ignore
    previous_txn_id: str = REQUIRED  # type: ignore
    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    ticket_sequence: int = REQUIRED  # type: ignore
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.TICKET,
        init=False,
    )
