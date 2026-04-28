"""Model for ConfidentialMPTSend transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.confidential_mpt_convert import (
    CIPHERTEXT_LENGTH,
    COMMITMENT_LENGTH,
    SEND_PROOF_LENGTH,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class ConfidentialMPTSend(Transaction):
    """
    Represents a ConfidentialMPTSend transaction.

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

    amount_commitment: str = REQUIRED  # type: ignore
    """Pedersen commitment to the amount being sent (64 bytes)."""

    balance_commitment: str = REQUIRED  # type: ignore
    """Pedersen commitment to the sender's remaining spending balance (64 bytes)."""

    auditor_encrypted_amount: Optional[str] = None
    """
    Ciphertext for the auditor. Required if sfAuditorEncryptionKey is
    present on the issuance.
    """

    credential_ids: Optional[List[str]] = None
    """
    Credential(s) to attach to the transaction for authorization purposes (XLS-70).
    Required if the destination account uses credential-based deposit authorization.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CONFIDENTIAL_SEND,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        # Validate sender != destination (temMALFORMED)
        if hasattr(self, "account") and hasattr(self, "destination"):
            if self.account == self.destination:
                errors["destination"] = "Sender cannot send to themselves"

        # Validate ciphertext lengths (temBAD_CIPHERTEXT)
        if len(self.sender_encrypted_amount) != CIPHERTEXT_LENGTH:
            errors["sender_encrypted_amount"] = (
                "sender_encrypted_amount must be 66 bytes (132 hex characters)"
            )

        if len(self.destination_encrypted_amount) != CIPHERTEXT_LENGTH:
            errors["destination_encrypted_amount"] = (
                "destination_encrypted_amount must be 66 bytes (132 hex characters)"
            )

        if len(self.issuer_encrypted_amount) != CIPHERTEXT_LENGTH:
            errors["issuer_encrypted_amount"] = (
                "issuer_encrypted_amount must be 66 bytes (132 hex characters)"
            )

        if (
            self.auditor_encrypted_amount is not None
            and len(self.auditor_encrypted_amount) != CIPHERTEXT_LENGTH
        ):
            errors["auditor_encrypted_amount"] = (
                "auditor_encrypted_amount must be 66 bytes (132 hex characters)"
            )

        # Validate commitment lengths (33 bytes = 66 hex for compressed point)
        if len(self.amount_commitment) != COMMITMENT_LENGTH:
            errors["amount_commitment"] = (
                "amount_commitment must be 33 bytes (66 hex characters)"
            )

        if len(self.balance_commitment) != COMMITMENT_LENGTH:
            errors["balance_commitment"] = (
                "balance_commitment must be 33 bytes (66 hex characters)"
            )

        # Validate zk_proof length (946 bytes for Send proof)
        if len(self.zk_proof) != SEND_PROOF_LENGTH:
            errors["zk_proof"] = (
                "zk_proof must be 946 bytes (1892 hex characters) for Send proof"
            )

        return errors
