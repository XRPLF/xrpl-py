"""Model for LoanBrokerCoverClawback transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from typing import Dict, Optional, Union

from typing_extensions import Self

from xrpl.models.amounts import (
    IssuedCurrencyAmount,
    MPTAmount,
    get_amount_value,
    is_xrp,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LoanBrokerCoverClawback(Transaction):
    """This transaction claws back First-Loss Capital from a Loan Broker"""

    loan_broker_id: Optional[str] = None
    """
    The Loan Broker ID from which to claw back First-Loss Capital. Must be provided if
    the Amount is an MPT, or Amount is an IOU and issuer is specified as the Account
    submitting the transaction.
    """

    amount: Optional[Union[IssuedCurrencyAmount, MPTAmount]] = None
    """
    The First-Loss Capital amount to clawback. If the amount is 0 or not provided,
    clawback funds up to LoanBroker.DebtTotal * LoanBroker.CoverRateMinimum.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_BROKER_COVER_CLAWBACK,
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

        if self.loan_broker_id is None and self.amount is None:
            parent_class_errors["LoanBrokerCoverClawback"] = (
                "No amount or loan broker ID specified."
            )

        if self.amount is not None:
            if is_xrp(self.amount):
                parent_class_errors["LoanBrokerCoverClawback:Amount"] = (
                    "Amount cannot be XRP."
                )
            elif get_amount_value(self.amount) < 0:
                parent_class_errors["LoanBrokerCoverClawback:Amount"] = (
                    "Amount must be greater than 0."
                )

        return parent_class_errors
