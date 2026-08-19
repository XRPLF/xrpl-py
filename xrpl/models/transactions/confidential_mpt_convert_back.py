"""Model for ConfidentialMPTConvertBack transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.confidential_mpt_constants import (
    BLINDING_FACTOR_LENGTH,
    CIPHERTEXT_LENGTH,
    COMMITMENT_LENGTH,
    CONVERT_BACK_PROOF_LENGTH,
    address_is_issuer,
    get_mpt_amount_error,
    get_mptoken_issuance_id_error,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType


@dataclass(frozen=True, kw_only=True)
# pylint: disable=too-many-instance-attributes
class ConfidentialMPTConvertBack(Transaction):
    """
    Represents a ConfidentialMPTConvertBack transaction.

    Convert confidential into public MPT value.
    - For a holder: restore public balance from CB_S.
    - For the issuer's second account: return confidential supply to issuer
      reserve.
    """

    account: str = REQUIRED
    """The account performing the conversion."""

    mptoken_issuance_id: str = REQUIRED
    """The unique identifier for the MPT issuance."""

    mpt_amount: int = REQUIRED
    """The plaintext amount to credit to the public balance."""

    holder_encrypted_amount: str = REQUIRED
    """Ciphertext to be subtracted from the holder's sfConfidentialBalanceSpending."""

    issuer_encrypted_amount: str = REQUIRED
    """Ciphertext to be subtracted from the issuer's mirror balance."""

    blinding_factor: str = REQUIRED
    """
    The 32-byte scalar value used to encrypt the amount. Used by validators
    to verify the ciphertexts match the plaintext MPTAmount.
    """

    balance_commitment: str = REQUIRED
    """
    Pedersen commitment to the holder's CURRENT confidential spending balance
    (33 bytes compressed).
    """

    zk_proof: str = REQUIRED
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

        # Guard each check against the REQUIRED sentinel so super()'s
        # "is not set" error surfaces first instead of a TypeError.
        if (
            self.blinding_factor is not REQUIRED
            and len(self.blinding_factor) != BLINDING_FACTOR_LENGTH
        ):
            errors["blinding_factor"] = (
                "blinding_factor must be 32 bytes (64 hex characters)"
            )

        if self.mpt_amount is not REQUIRED:
            amount_error = get_mpt_amount_error(self.mpt_amount, allow_zero=False)
            if amount_error is not None:
                errors["mpt_amount"] = amount_error

        if (
            self.holder_encrypted_amount is not REQUIRED
            and len(self.holder_encrypted_amount) != CIPHERTEXT_LENGTH
        ):
            errors["holder_encrypted_amount"] = (
                "holder_encrypted_amount must be 66 bytes (132 hex characters)"
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

        # Validate balance_commitment length (33 bytes = 66 hex for compressed point)
        if (
            self.balance_commitment is not REQUIRED
            and len(self.balance_commitment) != COMMITMENT_LENGTH
        ):
            errors["balance_commitment"] = (
                "balance_commitment must be 33 bytes (66 hex characters)"
            )

        # Validate zk_proof length (816 bytes for ConvertBack proof)
        if (
            self.zk_proof is not REQUIRED
            and len(self.zk_proof) != CONVERT_BACK_PROOF_LENGTH
        ):
            errors["zk_proof"] = (
                "zk_proof must be 816 bytes (1632 hex characters) for ConvertBack proof"
            )

        if self.mptoken_issuance_id is not REQUIRED:
            issuance_id_error = get_mptoken_issuance_id_error(self.mptoken_issuance_id)
            if issuance_id_error is not None:
                errors["mptoken_issuance_id"] = issuance_id_error
            elif self.account is not REQUIRED and address_is_issuer(
                self.mptoken_issuance_id, self.account
            ):
                # The issuer holds value only through its mirror balance, so it
                # cannot be the Account converting confidential value back to
                # public (temMALFORMED, ConfidentialMPTConvertBack.cpp preflight).
                errors["account"] = "The issuer cannot be the account of a ConvertBack"

        return errors
