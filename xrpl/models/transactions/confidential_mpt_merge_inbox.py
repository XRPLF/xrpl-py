"""Model for ConfidentialMPTMergeInbox transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.confidential_mpt_constants import (
    address_is_issuer,
    get_mptoken_issuance_id_error,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType


@dataclass(frozen=True, kw_only=True)
class ConfidentialMPTMergeInbox(Transaction):
    """
    Represents a ConfidentialMPTMergeInbox transaction.

    Moves all funds from the inbox balance into the spending balance, then
    resets the inbox to a canonical encrypted zero (EncZero). This ensures that
    proofs reference only stable spending balances and prevents staleness from
    incoming transfers.
    """

    account: str = REQUIRED
    """The account performing the merge."""

    mptoken_issuance_id: str = REQUIRED
    """The unique identifier for the MPT issuance."""

    transaction_type: TransactionType = field(
        default=TransactionType.CONFIDENTIAL_MERGE_INBOX,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.mptoken_issuance_id is not REQUIRED:
            issuance_id_error = get_mptoken_issuance_id_error(self.mptoken_issuance_id)
            if issuance_id_error is not None:
                errors["mptoken_issuance_id"] = issuance_id_error
            elif self.account is not REQUIRED and address_is_issuer(
                self.mptoken_issuance_id, self.account
            ):
                # The issuer has no personal confidential balance to merge, so it
                # cannot be the Account of a MergeInbox (temMALFORMED,
                # ConfidentialMPTMergeInbox.cpp preflight).
                errors["account"] = "The issuer cannot be the account of a MergeInbox"

        return errors
