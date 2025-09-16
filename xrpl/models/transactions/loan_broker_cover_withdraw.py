"""Model for LoanBrokerCoverWithdraw transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LoanBrokerCoverWithdraw(Transaction):
    """This transaction withdraws First-Loss Capital from a Loan Broker"""

    loan_broker_id: str = REQUIRED
    """
    The Loan Broker ID from which to withdraw First-Loss Capital.
    """

    amount: Amount = REQUIRED
    """
    The First-Loss Capital amount to withdraw.
    """

    destination: Optional[str] = None
    """
    An account to receive the assets. It must be able to receive the asset.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_BROKER_COVER_WITHDRAW,
        init=False,
    )
