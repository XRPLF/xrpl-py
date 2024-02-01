"""Models for the Ledger Object `Ticket`"""

from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Ticket(LedgerObject):
    """The model for the `Ticket` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    """
    The account that owns this Ticket. This field is required.
    """

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the owner directory links to this entry, in case
    the directory consists of multiple pages. This field is required.
    """

    previous_txn_id: str = REQUIRED  # type: ignore
    """
    The identifying hash of the transaction that most recently modified this entry.
    This field is required.
    """

    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    """
    The index of the ledger that contains the transaction that most recently modified
    this entry. This field is required.
    """

    ticket_sequence: int = REQUIRED  # type: ignore
    """
    The Sequence Number this Ticket sets aside. This field is required.
    """

    flags: int = 0
    """
    A bit-map of boolean flags. Flags is always 0 since there are no flags defined for
    Ticket entries.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.TICKET,
        init=False,
    )
