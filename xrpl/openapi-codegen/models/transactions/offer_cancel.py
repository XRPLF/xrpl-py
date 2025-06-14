"""Model for OfferCancel transaction type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OfferCancel(Transaction):
    """
    An OfferCancel transaction removes an Offer object from the XRP Ledger.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.OFFER_CANCEL, init=False
    )

    offer_sequence: int = REQUIRED
    """
    The sequence number (or Ticket number) of a previous OfferCreate transaction. If
    specified, cancel any offer object in the ledger that was created by that transaction.
    It is not considered an error if the offer specified does not exist.
    """
