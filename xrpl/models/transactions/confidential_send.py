"""Model for ConfidentialSend transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class ConfidentialSend(Transaction):
    """
    Represents a ConfidentialSend transaction.

    Performs a confidential transfer of MPT value between accounts while keeping
    the transfer amount hidden. The transferred amount is credited to the
    receiver's confidential inbox balance (CB_IN) to avoid proof staleness; the
    receiver may later merge these funds into the spending balance (CB_S) via
    ConfidentialMergeInbox.
    """

    account: str = REQUIRED  # type: ignore
    """The sender's XRPL account."""

    destination: str = REQUIRED  # type: ignore
    """The receiver's XRPL account."""

    mptoken_issuance_id: str = REQUIRED  # type: ignore
    """Identifier of the MPT issuance being transferred."""

    sender_encrypted_amount: str = REQUIRED  # type: ignore
    """Ciphertext used to homomorphically debit the sender's spending balance."""

    destination_encrypted_amount: str = REQUIRED  # type: ignore
    """Ciphertext credited to the receiver's inbox balance."""

    issuer_encrypted_amount: str = REQUIRED  # type: ignore
    """Ciphertext used to update the issuer mirror balance."""

    zk_proof: str = REQUIRED  # type: ignore
    """ZKP bundle establishing equality, linkage, and range sufficiency."""

    pedersen_commitment: str = REQUIRED  # type: ignore
    """A cryptographic commitment to the user's confidential spending balance."""

    auditor_encrypted_amount: Optional[str] = None
    """
    Ciphertext for the auditor. Required if sfAuditorElGamalPublicKey is
    present on the issuance.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CONFIDENTIAL_SEND,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if hasattr(self, "account") and hasattr(self, "destination"):
            if self.account == self.destination:
                errors["destination"] = "Sender cannot send to themselves"

        return errors
