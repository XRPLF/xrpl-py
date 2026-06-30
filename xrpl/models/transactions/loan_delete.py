"""Model for LoanDelete transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType


@dataclass(frozen=True, kw_only=True)
class LoanDelete(Transaction):
    """The transaction deletes an existing Loan object."""

    loan_id: str = REQUIRED
    """
    The ID of the Loan object to be deleted.
    This field is required.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_DELETE,
        init=False,
    )
