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
    """
    The sender of the Check. Cashing the Check debits this address's balance.
    This field is required.
    """

    destination: str = REQUIRED  # type: ignore
    """
    The intended recipient of the Check. Only this address can cash the Check, using a
    `CheckCash` transaction. This field is required.
    """

    destination_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the destination's owner directory links to this
    object, in case the directory consists of multiple pages.
    """

    destination_tag: Optional[int] = None
    """
    An arbitrary tag to further specify the destination for this Check, such as a
    hosted recipient at the destination address.
    """

    expiration: Optional[int] = None
    """
    Indicates the time after which this Check is considered expired. See Specifying
    Time for details.
    """

    invoice_id: Optional[str] = None
    """
    Arbitrary 256-bit hash provided by the sender as a specific reason or identifier
    for this Check.
    """

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the sender's owner directory links to this object,
    in case the directory consists of multiple pages. This field is required.
    """

    previous_txn_id: str = REQUIRED  # type: ignore
    """
    The identifying hash of the transaction that most recently modified this object.
    This field is required.
    """

    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    """
    The index of the ledger that contains the transaction that most recently modified
    this object. This field is required.
    """

    send_max: Union[str, IssuedCurrencyAmount] = REQUIRED  # type: ignore
    """
    The maximum amount of currency this Check can debit the sender. If the Check is
    successfully cashed, the destination is credited in the same currency for up to
    this amount. This field is required.
    """

    sequence: int = REQUIRED  # type: ignore
    """
    The sequence number of the `CheckCreate` transaction that created this check.
    This field is required.
    """

    source_tag: Optional[int] = None
    """
    An arbitrary tag to further specify the source for this Check, such as a hosted
    recipient at the sender's address.
    """

    flags: int = REQUIRED  # type: ignore
    """
    Flags is always 0 since there are no flags defined for Check entries.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.CHECK,
        init=False,
    )
    """
    The value 0x0043, mapped to the string `Check`, indicates that this object is a
    Check object.
    """
