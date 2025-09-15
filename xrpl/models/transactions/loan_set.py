"""Model for LoanSet transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import (
    Signer,
    Transaction,
    TransactionFlagInterface,
)
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class CounterpartySignature(BaseModel):
    """
    An inner object that contains the signature of the Lender over the transaction.
    The fields contained in this object are:
    """

    signing_pub_key: Optional[str] = None
    txn_signature: Optional[str] = None
    signers: Optional[List[Signer]] = None


class LoanSetFlag(int, Enum):
    """
    Enum for LoanSet Transaction Flags.

    Transactions of the LoanSet type support additional values in the Flags field.
    This enum represents those options.
    """

    TF_LOAN_OVER_PAYMENT = 0x00010000
    """
    Indicates that the loan supports overpayments.
    """


class LoanSetFlagInterface(TransactionFlagInterface):
    """
    Transactions of the LoanSet type support additional values in the Flags field.
    This TypedDict represents those options.
    """

    TF_LOAN_OVER_PAYMENT: bool


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LoanSet(Transaction):
    """This transaction creates a Loan"""

    loan_broker_id: str = REQUIRED  # type: ignore
    """
    The Loan Broker ID associated with the loan.
    """

    data: Optional[str] = None
    """
    Arbitrary metadata in hex format. The field is limited to 256 bytes.
    """

    counterparty: Optional[str] = None
    """The address of the counterparty of the Loan."""

    counterparty_signature: Optional[CounterpartySignature] = None
    """
    The signature of the counterparty over the transaction.
    """

    loan_origination_fee: Optional[int] = None
    """
    A nominal funds amount paid to the LoanBroker.Owner when the Loan is created.
    """

    loan_service_fee: Optional[int] = None
    """
    A nominal amount paid to the LoanBroker.Owner with every Loan payment.
    """

    late_payment_fee: Optional[int] = None
    """
    A nominal funds amount paid to the LoanBroker.Owner when a payment is late.
    """

    close_payment_fee: Optional[int] = None
    """
    A nominal funds amount paid to the LoanBroker.Owner when an early full repayment is
    made.
    """

    overpayment_fee: Optional[int] = None
    """
    A fee charged on overpayments in 1/10th basis points. Valid values are between 0
    and 100000 inclusive. (0 - 100%)
    """

    interest_rate: Optional[int] = None
    """
    Annualized interest rate of the Loan in in 1/10th basis points. Valid values are
    between 0 and 100000 inclusive. (0 - 100%)
    """

    late_interest_rate: Optional[int] = None
    """
    A premium added to the interest rate for late payments in in 1/10th basis points.
    Valid values are between 0 and 100000 inclusive. (0 - 100%)
    """

    close_interest_rate: Optional[int] = None
    """
    A Fee Rate charged for repaying the Loan early in 1/10th basis points. Valid values
    are between 0 and 100000 inclusive. (0 - 100%)
    """

    overpayment_interest_rate: Optional[int] = None
    """
    An interest rate charged on overpayments in 1/10th basis points. Valid values are
    between 0 and 100000 inclusive. (0 - 100%)
    """

    principal_requested: str = REQUIRED  # type: ignore
    """
    The principal amount requested by the Borrower.
    """

    start_date: int = REQUIRED  # type: ignore
    payment_total: Optional[int] = None
    """
    The total number of payments to be made against the Loan.
    """

    payment_interval: Optional[int] = None
    """
    Number of seconds between Loan payments.
    """

    grace_period: Optional[int] = None
    """
    The number of seconds after the Loan's Payment Due Date can be Defaulted.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_SET,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        parent_class_errors = {
            key: value
            for key, value in {
                **super()._get_errors(),
            }.items()
            if value is not None
        }

        if self.payment_interval is not None and self.payment_interval < 60:
            parent_class_errors["LoanSet:PaymentInterval"] = (
                "Payment interval must be at least 60 seconds."
            )

        if (
            self.grace_period is not None
            and self.payment_interval is not None
            and self.grace_period > self.payment_interval
        ):
            parent_class_errors["LoanSet:GracePeriod"] = (
                "Grace period must be less than the payment interval."
            )

        return parent_class_errors
