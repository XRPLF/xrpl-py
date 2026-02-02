"""Model for ConfidentialConvert transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init

# Length constants for validation (in hex characters)
HOLDER_ELGAMAL_PUBLIC_KEY_LENGTH = 64 * 2  # 64 bytes = 128 hex chars
BLINDING_FACTOR_LENGTH = 32 * 2  # 32 bytes = 64 hex chars
SCHNORR_PROOF_LENGTH = 65 * 2  # 65 bytes = 130 hex chars
EQUALITY_PROOF_LENGTH = 98 * 2  # 98 bytes = 196 hex chars (plaintext-ciphertext)


@require_kwargs_on_init
@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class ConfidentialConvert(Transaction):
    """
    Represents a ConfidentialConvert transaction.

    Converts a holder's own visible (public) MPT balance into confidential form.
    The converted amount is credited to the holder's confidential inbox balance
    (CB_IN) to avoid immediate proof staleness, requiring an explicit merge into
    the spending balance (CB_S) before use. This transaction also serves as the
    opt-in mechanism for confidential MPT participation: by executing it
    (including a zero-amount conversion), a holder's HolderElGamalPublicKey is
    recorded on their MPToken object, enabling the holder to receive and manage
    confidential funds.

    This transaction is a self-conversion only. Issuers introduce supply
    exclusively through existing XLS-33 public issuance mechanisms. The issuer's
    designated second account participates in confidential MPTs by executing
    ConfidentialConvert as a regular holder, with no special privileges. In all
    cases, OutstandingAmount (OA) and ConfidentialOutstandingAmount (COA) are
    maintained in plaintext according to existing invariants.
    """

    account: str = REQUIRED  # type: ignore
    """The account initiating the conversion."""

    mptoken_issuance_id: str = REQUIRED  # type: ignore
    """The unique identifier for the MPT issuance."""

    mpt_amount: int = REQUIRED  # type: ignore
    """The public plaintext amount to convert."""

    holder_encrypted_amount: str = REQUIRED  # type: ignore
    """ElGamal ciphertext credited to the holder's CB_IN."""

    issuer_encrypted_amount: str = REQUIRED  # type: ignore
    """ElGamal ciphertext credited to the issuer's mirror balance."""

    blinding_factor: str = REQUIRED  # type: ignore
    """
    The 32-byte scalar value used to encrypt the amount. Used by validators
    to verify the ciphertexts match the plaintext MPTAmount.
    """

    holder_elgamal_public_key: Optional[str] = None
    """
    The holder's ElGamal public key. Mandatory if the account has not yet
    registered a key (initialization). Forbidden if a key is already registered.
    """

    auditor_encrypted_amount: Optional[str] = None
    """
    ElGamal Ciphertext for the auditor. Required if sfAuditorElGamalPublicKey
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

        if self.holder_elgamal_public_key is not None and self.zk_proof is None:
            errors["zk_proof"] = (
                "zk_proof is required when registering a new holder public key"
            )

        if self.holder_elgamal_public_key is None and self.zk_proof is not None:
            errors["zk_proof"] = (
                "zk_proof should not be provided if not registering a "
                "holder public key"
            )

        if (
            self.holder_elgamal_public_key is not None
            and len(self.holder_elgamal_public_key) != HOLDER_ELGAMAL_PUBLIC_KEY_LENGTH
        ):
            errors["holder_elgamal_public_key"] = (
                "holder_elgamal_public_key must be 64 bytes (128 hex characters)"
            )

        if len(self.blinding_factor) != BLINDING_FACTOR_LENGTH:
            errors["blinding_factor"] = (
                "blinding_factor must be 32 bytes (64 hex characters)"
            )

        if self.zk_proof is not None and len(self.zk_proof) != SCHNORR_PROOF_LENGTH:
            errors["zk_proof"] = (
                "zk_proof must be 65 bytes (130 hex characters) for Schnorr Proof"
            )

        return errors
