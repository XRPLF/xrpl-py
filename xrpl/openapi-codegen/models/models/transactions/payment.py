"""Model for Payment transaction type."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.path_step import PathStep
from xrpl.models.payment_flag import PaymentFlag
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Payment(Transaction):
    """
    A Payment transaction represents a transfer of value from one account to another.
    (Depending on the path taken, this can involve additional exchanges of value, which
    occur atomically.) This transaction type can be used for several types of payments.
    Payments are also the only way to create accounts.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.PAYMENT, init=False
    )

    amount: Optional[Any] = REQUIRED
    """
    The maximum amount of currency to deliver. Partial payments can deliver less than this
    amount and still succeed; other payments fail unless they deliver the exact amount.
    """

    deliver_min: Optional[Any] = None
    """
    (Optional) Minimum amount of destination currency this transaction should deliver. Only
    valid if this is a partial payment. For non-XRP amounts, the nested field names are
    lower-case.
    """

    destination: str = REQUIRED
    """
    The unique address of the account receiving the payment.
    """

    destination_tag: Optional[int] = None
    """
    (Optional) Arbitrary tag that identifies the reason for the payment to the destination,
    or a hosted recipient to pay.
    """

    invoice_id: Optional[str] = None
    """
    (Optional) Arbitrary 256-bit hash representing a specific reason or identifier for this
    payment.
    """

    paths: Optional[List[List[PathStep]]] = None
    """
    (Optional, auto-fillable) Array of payment paths to be used for this transaction. Must
    be omitted for XRP-to-XRP transactions.
    """

    send_max: Optional[Any] = None
    """
    (Optional) Highest amount of source currency this transaction is allowed to cost,
    including transfer fees, exchange rates, and slippage. Does not include the XRP
    destroyed as a cost for submitting the transaction. For non-XRP amounts, the nested
    field names MUST be lower-case. Must be supplied for cross-currency/cross-issue
    payments. Must be omitted for XRP-to-XRP payments.
    """

    def _get_errors(self: Payment) -> Dict[str, str]:
        errors = super._get_errors()
        # This check is only applicable if the flag belongs to the `flags` field inherited from base Transaction.
        # For other cases such as `set_flag` or `clear_flag` field in account_info transaction, please fix accordingly.
        if (
            not self.has_flag(PaymentFlag.TF_PARTIAL_PAYMENT)
            and self.deliver_min is not None
        ):
            errors["Payment"] = (
                "`deliver_min` must not be set without flag `TF_PARTIAL_PAYMENT`"
            )
        return errors


class PaymentFlagInterface(FlagInterface):
    """
    Enum for Payment Transaction Flags.
    """

    TF_NO_RIPPLE_DIRECT: bool
    TF_PARTIAL_PAYMENT: bool
    TF_LIMIT_QUALITY: bool


class PaymentFlag(int, Enum):
    """
    Enum for Payment Transaction Flags.
    """

    TF_NO_RIPPLE_DIRECT = 0x00010000
    """
    Do not use the default path; only use paths included in the Paths field. This is intended to force the transaction to take arbitrage opportunities. Most clients do not need this.
    """

    TF_PARTIAL_PAYMENT = 0x00020000
    """
    If the specified Amount cannot be sent without spending more than SendMax, reduce the received amount instead of failing outright. See Partial Payments for more details.
    """

    TF_LIMIT_QUALITY = 0x00040000
    """
    Only take paths where all the conversions have an input:output ratio that is equal or better than the ratio of Amount:SendMax. See Limit Quality for details.
    """
