"""Model for LoanPay transaction type."""

from dataclasses import dataclass, field

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LoanPay(Transaction):
    """The Borrower submits a LoanPay transaction to make a Payment on the Loan."""

    loan_id: str = REQUIRED
    """
    The ID of the Loan object to be paid to.
    This field is required.
    """

    amount: Amount = REQUIRED
    """
    The amount of funds to pay.
    This field is required.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_PAY,
        init=False,
    )
