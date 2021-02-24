"""
Represents a Payment transaction on the XRP Ledger.

A Payment transaction represents a transfer of value from one account to another.
(Depending on the path taken, this can involve additional exchanges of value, which
occur atomically.) This transaction type can be used for several types of payments.

Payments are also the only way to create accounts.

`See Payment <https://xrpl.org/payment.html>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from xrpl.models.amount import Amount, is_xrp
from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType


class PaymentFlag(int, Enum):
    """
    Transactions of the Payment type support additional values in the Flags field.
    This enum represents those options.

    `See Payment Flags <https://xrpl.org/payment.html#payment-flags>`_
    """

    TF_NO_DIRECT_RIPPLE = 0x00010000
    TF_PARTIAL_PAYMENT = 0x00020000
    TF_LIMIT_QUALITY = 0x00040000


@dataclass(frozen=True)
class Payment(Transaction):
    """
    Represents a Payment transaction on the XRP Ledger.

    A Payment transaction represents a transfer of value from one account to another.
    (Depending on the path taken, this can involve additional exchanges of value, which
    occur atomically.) This transaction type can be used for several types of payments.

    Payments are also the only way to create accounts.

    `See Payment <https://xrpl.org/payment.html>`_
    """

    amount: Amount = REQUIRED
    destination: str = REQUIRED
    destination_tag: Optional[int] = None
    invoice_id: Optional[str] = None  # TODO: should be a 256 bit hash
    paths: Optional[List[Any]] = None
    send_max: Optional[Amount] = None
    deliver_min: Optional[Amount] = None
    transaction_type: TransactionType = TransactionType.Payment

    def _get_errors(self: Payment) -> Dict[str, str]:
        errors = super()._get_errors()

        # XRP transaction errors
        if is_xrp(self.amount) and self.send_max is None:
            if self.paths is not None:
                errors["paths"] = "An XRP-to-XRP payment cannot contain paths."
            if self.account == self.destination:
                errors["destination"] = (
                    "An XRP payment transaction cannot have the same sender and "
                    "destination."
                )

        # partial payment errors
        elif self.has_flag(PaymentFlag.TF_PARTIAL_PAYMENT) and self.send_max is None:
            errors["send_max"] = "A partial payment must have a `send_max` value."
        elif self.deliver_min is not None and not self.has_flag(
            PaymentFlag.TF_PARTIAL_PAYMENT
        ):
            errors[
                "deliver_min"
            ] = "A non-partial payment cannot have a `deliver_min` field."

        elif (
            is_xrp(self.amount)
            and is_xrp(self.send_max)
            and not self.has_flag(PaymentFlag.TF_PARTIAL_PAYMENT)
        ):
            errors["send_max"] = (
                "A non-partial payment cannot have both `amount` and `send_max` be "
                "XRP."
            )

        # currency conversion errors
        elif self.account == self.destination:
            if self.send_max is None:
                errors[
                    "send_max"
                ] = "A currency conversion requires a `send_max` value."

        return errors
