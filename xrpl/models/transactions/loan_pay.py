"""Model for LoanPay transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from typing_extensions import Self

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class LoanPayFlag(int, Enum):
    """
    Enum for LoanPay Transaction Flags.

    Transactions of the LoanPay type support additional values in the flags field
    """

    TF_LOAN_OVERPAYMENT = 0x00010000
    """
    Indicates that the remaining payment amount should be treated as an overpayment.
    """

    TF_LOAN_FULL_PAYMENT = 0x00020000
    """
    Indicates that the borrower is making a full early repayment.
    """

    TF_LOAN_LATE_PAYMENT = 0x00040000
    """
    Indicates that the borrower is making a late loan payment.
    """


class LoanPayFlagInterface(TransactionFlagInterface):
    """
    Transactions of the LoanPay type support additional values in the Flags field.
    This TypedDict represents those options.
    """

    TF_LOAN_OVERPAYMENT: bool
    TF_LOAN_FULL_PAYMENT: bool
    TF_LOAN_LATE_PAYMENT: bool


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

    _VALID_FLAGS_MASK = 0x00070000

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.flags is not None and isinstance(self.flags, int):
            # Check for unrecognized flags (bits set outside valid mask)
            if self.flags & ~self._VALID_FLAGS_MASK:
                errors["LoanPay:Flags"] = "Unrecognised flag in the LoanPay transaction"
            # Check that at most one flag is enabled
            elif bin(self.flags & self._VALID_FLAGS_MASK).count("1") > 1:
                errors["LoanPay:Flags"] = (
                    "Only one flag must be enabled in the LoanPay transaction"
                )

        return errors
