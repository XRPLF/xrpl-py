"""
Represents an OfferCancel transaction on the XRP Ledger.

An OfferCancel transaction removes an Offer object from the XRP Ledger.

`See OfferCancel <https://xrpl.org/offercancel.html>`_
"""
from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OfferCancel(Transaction):
    """
    Represents an OfferCancel transaction on the XRP Ledger.

    An OfferCancel transaction removes an Offer object from the XRP Ledger.

    See https://xrpl.org/offercancel.html.
    """

    offer_sequence: int = REQUIRED  # type: ignore
    transaction_type: TransactionType = field(
        default=TransactionType.OFFER_CANCEL,
        init=False,
    )
