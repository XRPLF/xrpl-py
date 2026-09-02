"""Model for LoanBrokerCoverWithdraw transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import validate_credential_ids


@dataclass(frozen=True, kw_only=True)
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

    destination_tag: Optional[int] = None
    """
    An arbitrary `destination tag
    <https://xrpl.org/source-and-destination-tags.html>`_ that
    identifies the reason for the Payment, or a hosted recipient to pay.
    """

    credential_ids: Optional[List[str]] = None
    """
    Credential(s) to attach for credential-based deposit preauthorization (XLS-70)
    when the destination requires them.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_BROKER_COVER_WITHDRAW,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        errors.update(validate_credential_ids(self.credential_ids))

        return errors
