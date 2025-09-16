"""Model for LoanManage transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from enum import Enum

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class LoanManageFlag(int, Enum):
    """
    Enum for LoanManage Transaction Flags.

    Transactions of the LoanManage type support additional values in the Flags field.
    This enum represents those options.
    """

    TF_LOAN_DEFAULT = 0x00010000
    """
    Indicates that the Loan should be defaulted.
    """

    TF_LOAN_IMPAIR = 0x00020000
    """
    Indicates that the Loan should be impaired.
    """

    TF_LOAN_UNIMPAIR = 0x00040000
    """
    Indicates that the Loan should be unimpaired.
    """


class LoanManageFlagInterface(TransactionFlagInterface):
    """
    Transactions of the LoanManage type support additional values in the Flags field.
    This TypedDict represents those options.
    """

    TF_LOAN_DEFAULT: bool
    TF_LOAN_IMPAIR: bool
    TF_LOAN_UNIMPAIR: bool


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LoanManage(Transaction):
    """The transaction updates an existing Loan object."""

    loan_id: str = REQUIRED
    """
    The ID of the Loan object to be updated.
    This field is required.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_MANAGE,
        init=False,
    )
