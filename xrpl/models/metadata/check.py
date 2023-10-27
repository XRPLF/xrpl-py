"""Models for the Metadata Object `Check`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Check(LedgerObject):
    """
    The model for the `Check` Ledger Object when
    represented in a transaction's metadata.
    """

    account: Optional[str] = None
    destination: Optional[str] = None
    # always 0
    flags: Optional[int] = None
    owner_node: Optional[str] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    send_max: Optional[Union[str, IssuedCurrencyAmount]] = None
    sequence: Optional[int] = None
    destination_node: Optional[str] = None
    destination_tag: Optional[int] = None
    expiration: Optional[int] = None
    invoice_id: Optional[str] = None
    source_tag: Optional[int] = None
