"""Model for ConfidentialMPTConvert transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED

# Length constants are defined once in confidential_mpt_constants and re-exported
# here for backward compatibility with existing imports.
from xrpl.models.transactions.confidential_mpt_constants import (
    BLINDING_FACTOR_LENGTH,
    CIPHERTEXT_LENGTH,
    CLAWBACK_PROOF_LENGTH,
    COMMITMENT_LENGTH,
    CONVERT_BACK_PROOF_LENGTH,
    HOLDER_ENCRYPTION_KEY_LENGTH,
    SCHNORR_PROOF_LENGTH,
    SEND_PROOF_LENGTH,
    address_is_issuer,
    get_mpt_amount_error,
    get_mptoken_issuance_id_error,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType

__all__ = [
    "ConfidentialMPTConvert",
    "BLINDING_FACTOR_LENGTH",
    "CIPHERTEXT_LENGTH",
    "CLAWBACK_PROOF_LENGTH",
    "COMMITMENT_LENGTH",
    "CONVERT_BACK_PROOF_LENGTH",
    "HOLDER_ENCRYPTION_KEY_LENGTH",
    "SCHNORR_PROOF_LENGTH",
    "SEND_PROOF_LENGTH",
]


@dataclass(frozen=True, kw_only=True)
# pylint: disable=too-many-instance-attributes
class ConfidentialMPTConvert(Transaction):
    """
    Represents a ConfidentialMPTConvert transaction.

    Converts a holder's own visible (public) MPT balance into confidential form.
    The converted amount is credited to the holder's confidential inbox balance
    (CB_IN) to avoid immediate proof staleness, requiring an explicit merge into
    the spending balance (CB_S) before use. This transaction also serves as the
    opt-in mechanism for confidential MPT participation: by executing it
    (including a zero-amount conversion), a holder's HolderEncryptionKey is
    recorded on their MPToken object, enabling the holder to receive and manage
    confidential funds.

    This transaction is a self-conversion only. Issuers introduce supply
    exclusively through existing XLS-33 public issuance mechanisms. The issuer's
    designated second account participates in confidential MPTs by executing
    ConfidentialConvert as a regular holder, with no special privileges. In all
    cases, OutstandingAmount (OA) and ConfidentialOutstandingAmount (COA) are
    maintained in plaintext according to existing invariants.
    """

    account: str = REQUIRED
    """The account initiating the conversion."""

    mptoken_issuance_id: str = REQUIRED
    """The unique identifier for the MPT issuance."""

    mpt_amount: int = REQUIRED
    """The public plaintext amount to convert."""

    holder_encrypted_amount: str = REQUIRED
    """ElGamal ciphertext credited to the holder's CB_IN."""

    issuer_encrypted_amount: str = REQUIRED
    """ElGamal ciphertext credited to the issuer's mirror balance."""

    blinding_factor: str = REQUIRED
    """
    The 32-byte scalar value used to encrypt the amount. Used by validators
    to verify the ciphertexts match the plaintext MPTAmount.
    """

    holder_encryption_key: Optional[str] = None
    """
    The holder's ElGamal public key. Mandatory if the account has not yet
    registered a key (initialization). Forbidden if a key is already registered.
    """

    auditor_encrypted_amount: Optional[str] = None
    """
    ElGamal Ciphertext for the auditor. Required if sfAuditorEncryptionKey
    is present on the issuance.
    """

    zk_proof: Optional[str] = None
    """
    A Schnorr Proof of Knowledge (PoK): prove the knowledge of the private key
    for the provided ElGamal Public Key.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CONFIDENTIAL_CONVERT,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.holder_encryption_key is not None and self.zk_proof is None:
            errors["zk_proof"] = (
                "zk_proof is required when registering a new holder public key"
            )

        if self.holder_encryption_key is None and self.zk_proof is not None:
            errors["zk_proof"] = (
                "zk_proof should not be provided if not registering a "
                "holder public key"
            )

        if (
            self.holder_encryption_key is not None
            and len(self.holder_encryption_key) != HOLDER_ENCRYPTION_KEY_LENGTH
        ):
            errors["holder_encryption_key"] = (
                "holder_encryption_key must be 33 bytes (66 hex characters)"
            )

        # Guard REQUIRED fields against the sentinel so super()'s "is not set"
        # error surfaces first instead of a TypeError.
        if (
            self.blinding_factor is not REQUIRED
            and len(self.blinding_factor) != BLINDING_FACTOR_LENGTH
        ):
            errors["blinding_factor"] = (
                "blinding_factor must be 32 bytes (64 hex characters)"
            )

        if self.zk_proof is not None and len(self.zk_proof) != SCHNORR_PROOF_LENGTH:
            errors["zk_proof"] = (
                "zk_proof must be 64 bytes (128 hex characters) for Schnorr Proof"
            )

        if self.mpt_amount is not REQUIRED:
            # A zero amount is permitted here on purpose: rippled allows a
            # zero-amount Convert to register the holder's ElGamal key and
            # initialize the confidential-balance fields.
            amount_error = get_mpt_amount_error(self.mpt_amount, allow_zero=True)
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

        if self.mptoken_issuance_id is not REQUIRED:
            issuance_id_error = get_mptoken_issuance_id_error(self.mptoken_issuance_id)
            if issuance_id_error is not None:
                errors["mptoken_issuance_id"] = issuance_id_error
            elif self.account is not REQUIRED and address_is_issuer(
                self.mptoken_issuance_id, self.account
            ):
                # The issuer converts through its mirror balances, not a personal
                # confidential balance, so it cannot be the Account of a Convert
                # (temMALFORMED, ConfidentialMPTConvert.cpp preflight).
                errors["account"] = "The issuer cannot be the account of a Convert"

        return errors
