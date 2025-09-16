"""Model for LoanBrokerSet transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LoanBrokerSet(Transaction):
    """This transaction creates and updates a Loan Broker"""

    vault_id: str = REQUIRED
    """
    The Vault ID that the Lending Protocol will use to access liquidity.
    This field is required.
    """

    loan_broker_id: Optional[str] = None
    """
    The Loan Broker ID that the transaction is modifying.
    """

    data: Optional[str] = None
    """
    Arbitrary metadata in hex format. The field is limited to 256 bytes.
    """

    management_fee_rate: Optional[int] = None
    """
    The 1/10th basis point fee charged by the Lending Protocol Owner.
    Valid values are between 0 and 10000 inclusive.
    """

    debt_maximum: Optional[int] = None
    """
    The maximum amount the protocol can owe the Vault.
    The default value of 0 means there is no limit to the debt. Must not be negative.
    """

    cover_rate_minimum: Optional[int] = None
    """
    The 1/10th basis point DebtTotal that the first loss capital must cover.
    Valid values are between 0 and 100000 inclusive.
    """

    cover_rate_liquidation: Optional[int] = None
    """
    The 1/10th basis point of minimum required first loss capital liquidated to cover a
    Loan default. Valid values are between 0 and 100000 inclusive.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_BROKER_SET,
        init=False,
    )
