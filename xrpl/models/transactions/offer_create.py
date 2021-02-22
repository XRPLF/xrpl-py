"""
Represents an OfferCreate transaction on the XRP Ledger. An OfferCreate transaction is
effectively a limit order. It defines an intent to exchange currencies, and creates an
Offer object if not completely fulfilled when placed. Offers can be partially fulfilled.

See https://xrpl.org/offercreate.html.
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Optional

from xrpl.models.amount import Amount
from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType


@dataclass(frozen=True)
class OfferCreate(Transaction):
    """
    Represents an OfferCreate transaction on the XRP Ledger. An OfferCreate
    transaction is effectively a limit order. It defines an intent to exchange
    currencies, and creates an Offer object if not completely fulfilled when
    placed. Offers can be partially fulfilled.

    See https://xrpl.org/offercreate.html.
    """

    taker_gets: Amount = REQUIRED
    taker_pays: Amount = REQUIRED
    expiration: Optional[int] = None
    offer_sequence: Optional[int] = None
    transaction_type: str = TransactionType.OfferCreate
