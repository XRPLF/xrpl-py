"""
Represents a PaymentChannelFund transaction on the XRP Ledger.
A PaymentChannelFund transaction adds additional XRP to an open payment channel,
and optionally updates the expiration time of the channel. Only the source address
of the channel can use this transaction.

`See PaymentChannelFund <https://xrpl.org/paymentchannelfund.html>`_
"""
from dataclasses import dataclass
from typing import Optional

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType


@dataclass(frozen=True)
class PaymentChannelFund(Transaction):
    """
    Represents a PaymentChannelFund transaction on the XRP Ledger.
    A PaymentChannelFund transaction adds additional XRP to an open payment channel,
    and optionally updates the expiration time of the channel. Only the source address
    of the channel can use this transaction.

    `See PaymentChannelFund <https://xrpl.org/paymentchannelfund.html>`_
    """

    channel: str = REQUIRED
    amount: str = REQUIRED
    expiration: Optional[int] = None
    transaction_type: TransactionType = TransactionType.PaymentChannelFund
