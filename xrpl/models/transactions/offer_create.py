"""Model for OfferCreate transaction type."""
from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OfferCreate(Transaction):
    """
    Represents an `OfferCreate <https://xrpl.org/offercreate.html>`_ transaction,
    which executes a limit order in the `decentralized exchange
    <https://xrpl.org/decentralized-exchange.html>`_. If the specified exchange
    cannot be completely fulfilled, it creates an Offer object for the remainder.
    Offers can be partially fulfilled.
    """

    #: The amount and type of currency being provided by the sender of this
    #: transaction. This field is required.
    taker_gets: Amount = REQUIRED  # type: ignore
    #: The amount and type of currency the sender of this transaction wants in
    #: exchange for the full ``taker_gets`` amount. This field is required.
    taker_pays: Amount = REQUIRED  # type: ignore

    #: Time after which the offer is no longer active, in seconds since the
    #: Ripple Epoch.
    expiration: Optional[int] = None

    #: The Sequence number (or Ticket number) of a previous OfferCreate to cancel
    #: when placing this Offer.
    offer_sequence: Optional[int] = None

    transaction_type: TransactionType = field(
        default=TransactionType.OFFER_CREATE,
        init=False,
    )
