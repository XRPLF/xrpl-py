"""Model for LoanBrokerDelete transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LoanBrokerDelete(Transaction):
    """This transaction deletes a Loan Broker"""

    loan_broker_id: str = REQUIRED
    """
    The Loan Broker ID that the transaction is deleting.
    This field is required.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_BROKER_DELETE,
        init=False,
    )
