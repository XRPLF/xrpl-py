"""Model for CheckCreate transaction type."""

from dataclasses import dataclass, field
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class CheckCreate(Transaction):
    """
    Create a Check object in the ledger, which is a deferred payment that can be cashed by
    its intended destination. The sender of this transaction is the sender of the Check.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CHECK_CREATE, init=False
    )

    destination: str = REQUIRED
    """
    The unique address of the account that can cash the Check.
    """

    send_max: Optional[Any] = REQUIRED
    """
    Maximum amount of source currency the Check is allowed to debit the sender, including
    transfer fees on non-XRP currencies. The Check can only credit the destination with the
    same currency (from the same issuer, for non-XRP currencies). For non-XRP amounts, the
    nested field names MUST be lower-case.
    """

    destination_tag: Optional[int] = None
    """
    (Optional) Arbitrary tag that identifies the reason for the Check, or a hosted recipient
    to pay.
    """

    expiration: Optional[int] = None
    """
    (Optional) Time after which the Check is no longer valid, in seconds since the Ripple
    Epoch.
    """

    invoice_id: Optional[str] = None
    """
    (Optional) Arbitrary 256-bit hash representing a specific reason or identifier for this
    Check.
    """
