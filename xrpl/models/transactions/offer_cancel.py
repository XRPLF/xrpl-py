"""
Represents an OfferCancel transaction on the XRP Ledger.

An OfferCancel transaction removes an Offer object from the XRP Ledger.

`See OfferCancel <https://xrpl.org/offercancel.html>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Optional

from xrpl.models.transactions.transaction import Transaction, TransactionType


@dataclass(frozen=True)
class OfferCancel(Transaction):
    """
    Represents an OfferCancel transaction on the XRP Ledger.

    An OfferCancel transaction removes an Offer object from the XRP Ledger.

    See https://xrpl.org/offercancel.html.
    """

    offer_sequence: Optional[int] = None
    transaction_type: str = TransactionType.OfferCancel
