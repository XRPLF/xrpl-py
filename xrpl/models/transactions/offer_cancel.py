"""Model for OfferCancel transaction type."""
from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OfferCancel(Transaction):
    """
    Represents an `OfferCancel <https://xrpl.org/offercancel.html>`_ transaction,
    which removes an Offer object from the `decentralized exchange
    <https://xrpl.org/decentralized-exchange.html>`_.
    """

    #: The Sequence number (or Ticket number) of a previous OfferCreate
    #: transaction. If specified, cancel any Offer object in the ledger that was
    #: created by that transaction. It is not considered an error if the Offer
    #: specified does not exist.
    offer_sequence: int = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.OFFER_CANCEL,
        init=False,
    )
