"""Model for ConfidentialMPTSend transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.confidential_mpt_constants import (
    CIPHERTEXT_LENGTH,
    COMMITMENT_LENGTH,
    SEND_PROOF_LENGTH,
    address_is_issuer,
    get_mptoken_issuance_id_error,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import validate_credential_ids


@dataclass(frozen=True, kw_only=True)
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

    account: str = REQUIRED
    """The sender's XRPL account."""

    destination: str = REQUIRED
    """The receiver's XRPL account."""

    destination_tag: Optional[int] = None
    """
    An arbitrary tag that identifies the reason for the transfer, or a hosted
    recipient at the destination account.
    """

    mptoken_issuance_id: str = REQUIRED
    """Identifier of the MPT issuance being transferred."""

    sender_encrypted_amount: str = REQUIRED
    """Ciphertext used to homomorphically debit the sender's spending balance."""

    destination_encrypted_amount: str = REQUIRED
    """Ciphertext credited to the receiver's inbox balance."""

    issuer_encrypted_amount: str = REQUIRED
    """Ciphertext used to update the issuer mirror balance."""

    zk_proof: str = REQUIRED
    """ZKP bundle establishing equality, linkage, and range sufficiency."""

    amount_commitment: str = REQUIRED
    """Pedersen commitment to the amount being sent (33 bytes)."""

    balance_commitment: str = REQUIRED
    """Pedersen commitment to the sender's remaining spending balance (33 bytes)."""

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

        # Validate sender != destination (temMALFORMED). Guard against the
        # REQUIRED sentinel so super()'s "is not set" error surfaces first.
        if (
            self.account is not REQUIRED
            and self.destination is not REQUIRED
            and self.account == self.destination
        ):
            errors["destination"] = "Sender cannot send to themselves"

        # XLS-70 credentials, when present, must be a valid list (max length,
        # uniqueness, hex format) — matches rippled's credentials::checkFields.
        errors.update(validate_credential_ids(self.credential_ids))

        # Validate ciphertext lengths (temBAD_CIPHERTEXT)
        if (
            self.sender_encrypted_amount is not REQUIRED
            and len(self.sender_encrypted_amount) != CIPHERTEXT_LENGTH
        ):
            errors["sender_encrypted_amount"] = (
                "sender_encrypted_amount must be 66 bytes (132 hex characters)"
            )

        if (
            self.destination_encrypted_amount is not REQUIRED
            and len(self.destination_encrypted_amount) != CIPHERTEXT_LENGTH
        ):
            errors["destination_encrypted_amount"] = (
                "destination_encrypted_amount must be 66 bytes (132 hex characters)"
            )

        if (
            self.issuer_encrypted_amount is not REQUIRED
            and len(self.issuer_encrypted_amount) != CIPHERTEXT_LENGTH
        ):
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
        if (
            self.amount_commitment is not REQUIRED
            and len(self.amount_commitment) != COMMITMENT_LENGTH
        ):
            errors["amount_commitment"] = (
                "amount_commitment must be 33 bytes (66 hex characters)"
            )

        if (
            self.balance_commitment is not REQUIRED
            and len(self.balance_commitment) != COMMITMENT_LENGTH
        ):
            errors["balance_commitment"] = (
                "balance_commitment must be 33 bytes (66 hex characters)"
            )

        # Validate zk_proof length (946 bytes for Send proof)
        if self.zk_proof is not REQUIRED and len(self.zk_proof) != SEND_PROOF_LENGTH:
            errors["zk_proof"] = (
                "zk_proof must be 946 bytes (1892 hex characters) for Send proof"
            )

        if self.mptoken_issuance_id is not REQUIRED:
            issuance_id_error = get_mptoken_issuance_id_error(self.mptoken_issuance_id)
            if issuance_id_error is not None:
                errors["mptoken_issuance_id"] = issuance_id_error
            else:
                # A ConfidentialMPTSend only moves value holder<->holder, so the
                # issuer cannot be the Account or the Destination (temMALFORMED,
                # ConfidentialMPTSend.cpp preflight).
                if self.account is not REQUIRED and address_is_issuer(
                    self.mptoken_issuance_id, self.account
                ):
                    errors["account"] = "The issuer cannot be the sender of a Send"
                if self.destination is not REQUIRED and address_is_issuer(
                    self.mptoken_issuance_id, self.destination
                ):
                    errors["destination"] = (
                        "The issuer cannot be the destination of a Send"
                    )

        return errors
