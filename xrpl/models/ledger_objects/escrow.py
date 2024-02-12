"""Models for the Ledger Object `Escrow`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import HasPreviousTxnID, LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Escrow(LedgerObject, HasPreviousTxnID):
    """The model for the `Escrow` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    """
    The address of the owner (sender) of this escrow. This is the account that provided
    the XRP, and gets it back if the escrow is canceled. This field is required.
    """

    amount: str = REQUIRED  # type: ignore
    """
    The amount of XRP, in drops, currently held in the escrow. This field is required.
    """

    destination: str = REQUIRED  # type: ignore
    """
    The destination address where the XRP is paid if the escrow is successful.
    This field is required.
    """

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the sender's owner directory links to this entry,
    in case the directory consists of multiple pages. This field is required.
    """

    condition: Optional[str] = None
    """
    A PREIMAGE-SHA-256 crypto-condition , as hexadecimal. If present, the `EscrowFinish`
    transaction must contain a fulfillment that satisfies this condition.
    """

    cancel_after: Optional[int] = None
    """
    The escrow can be canceled if and only if this field is present and the time it
    specifies has passed. Specifically, this is specified as seconds since the Ripple
    Epoch and it "has passed" if it's earlier than the close time of the previous
    validated ledger.
    """

    destination_node: Optional[str] = None
    """
    A hint indicating which page of the destination's owner directory links to this
    object, in case the directory consists of multiple pages. Omitted on escrows
    created before enabling the fix1523 amendment.
    """

    destination_tag: Optional[int] = None
    """
    An arbitrary tag to further specify the destination for this escrow, such as a
    hosted recipient at the destination address.
    """

    finish_after: Optional[int] = None
    """
    The time, in seconds since the Ripple Epoch, after which this escrow can be
    finished. Any `EscrowFinish` transaction before this time fails. (Specifically, this
    is compared with the close time of the previous validated ledger.)
    """

    source_tag: Optional[int] = None
    """
    An arbitrary tag to further specify the source for this escrow, such as a hosted
    recipient at the owner's address.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.ESCROW, init=False
    )
