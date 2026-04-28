"""Model for ConfidentialMPTConvertBack transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.confidential_mpt_convert import (
    BLINDING_FACTOR_LENGTH,
    CIPHERTEXT_LENGTH,
    COMMITMENT_LENGTH,
    CONVERT_BACK_PROOF_LENGTH,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class ConfidentialMPTConvertBack(Transaction):
    """
    Represents a ConfidentialMPTConvertBack transaction.

    Convert confidential into public MPT value.
    - For a holder: restore public balance from CB_S.
    - For the issuer's second account: return confidential supply to issuer
      reserve.
    """

    account: str = REQUIRED  # type: ignore
    """The account performing the conversion."""

    mptoken_issuance_id: str = REQUIRED  # type: ignore
    """The unique identifier for the MPT issuance."""

    mpt_amount: int = REQUIRED  # type: ignore
    """The plaintext amount to credit to the public balance."""

    holder_encrypted_amount: str = REQUIRED  # type: ignore
    """Ciphertext to be subtracted from the holder's sfConfidentialBalanceSpending."""

    issuer_encrypted_amount: str = REQUIRED  # type: ignore
    """Ciphertext to be subtracted from the issuer's mirror balance."""

    blinding_factor: str = REQUIRED  # type: ignore
    """
    The 32-byte scalar value used to encrypt the amount. Used by validators
    to verify the ciphertexts match the plaintext MPTAmount.
    """

    balance_commitment: str = REQUIRED  # type: ignore
    """
    Pedersen commitment to the holder's CURRENT confidential spending balance
    (64 bytes uncompressed).
    """

    zk_proof: str = REQUIRED  # type: ignore
    """
    Complete proof (816 bytes) consisting of:
    - Compact sigma proof (128 bytes): proves balance ownership and commitment
      linkage under a single Fiat-Shamir challenge
    - Bulletproof (688 bytes): proves the remaining balance is in valid range
    """

    auditor_encrypted_amount: Optional[str] = None
    """
    Ciphertext for the auditor. Required if sfAuditorEncryptionKey is
    present on the issuance.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CONFIDENTIAL_CONVERT_BACK,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if len(self.blinding_factor) != BLINDING_FACTOR_LENGTH:
            errors["blinding_factor"] = (
                "blinding_factor must be 32 bytes (64 hex characters)"
            )

        if self.mpt_amount <= 0:
            errors["mpt_amount"] = "mpt_amount cannot be zero or negative"

        if len(self.holder_encrypted_amount) != CIPHERTEXT_LENGTH:
            errors["holder_encrypted_amount"] = (
                "holder_encrypted_amount must be 66 bytes (132 hex characters)"
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

        # Validate balance_commitment length (33 bytes = 66 hex for compressed point)
        if len(self.balance_commitment) != COMMITMENT_LENGTH:
            errors["balance_commitment"] = (
                "balance_commitment must be 33 bytes (66 hex characters)"
            )

        # Validate zk_proof length (816 bytes for ConvertBack proof)
        if len(self.zk_proof) != CONVERT_BACK_PROOF_LENGTH:
            errors["zk_proof"] = (
                "zk_proof must be 816 bytes (1632 hex characters) for ConvertBack proof"
            )

        return errors
