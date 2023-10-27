"""Models for the Ledger Object `Check`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Check(LedgerObject):
    """The model for the `Check` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    destination: str = REQUIRED  # type: ignore
    # always 0
    flags: int = REQUIRED  # type: ignore
    owner_node: str = REQUIRED  # type: ignore
    previous_txn_id: str = REQUIRED  # type: ignore
    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    send_max: Union[str, IssuedCurrencyAmount] = REQUIRED  # type: ignore
    sequence: int = REQUIRED  # type: ignore
    destination_node: Optional[str] = None
    destination_tag: Optional[int] = None
    expiration: Optional[int] = None
    invoice_id: Optional[str] = None
    source_tag: Optional[int] = None
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.CHECK,
        init=False,
    )
