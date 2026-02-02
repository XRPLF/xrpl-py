"""Model for ConfidentialMergeInbox transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class ConfidentialMergeInbox(Transaction):
    """
    Represents a ConfidentialMergeInbox transaction.

    Moves all funds from the inbox balance into the spending balance, then
    resets the inbox to a canonical encrypted zero (EncZero). This ensures that
    proofs reference only stable spending balances and prevents staleness from
    incoming transfers.
    """

    account: str = REQUIRED  # type: ignore
    """The account performing the merge."""

    mptoken_issuance_id: str = REQUIRED  # type: ignore
    """The unique identifier for the MPT issuance."""

    transaction_type: TransactionType = field(
        default=TransactionType.CONFIDENTIAL_MERGE_INBOX,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        return errors
