"""Models for the Ledger Object `DepositPreauth`"""

from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DepositPreauth(LedgerObject):
    """The model for the `DepositPreauth` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    authorize: str = REQUIRED  # type: ignore
    # always 0
    flags: int = REQUIRED  # type: ignore
    owner_node: str = REQUIRED  # type: ignore
    previous_txn_id: str = REQUIRED  # type: ignore
    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.DEPOSIT_PREAUTH,
        init=False,
    )
