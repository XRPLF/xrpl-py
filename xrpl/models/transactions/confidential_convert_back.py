"""Model for ConfidentialConvertBack transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.confidential_convert import BLINDING_FACTOR_LENGTH
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class ConfidentialConvertBack(Transaction):
    """
    Represents a ConfidentialConvertBack transaction.

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

    pedersen_commitment: str = REQUIRED  # type: ignore
    """A cryptographic commitment to the user's confidential spending balance."""

    zk_proof: str = REQUIRED  # type: ignore
    """
    A bundle containing the Pedersen Linkage Proof (linking the ElGamal balance
    to the commitment) and the Range Proof.
    """

    auditor_encrypted_amount: Optional[str] = None
    """
    Ciphertext for the auditor. Required if sfAuditorElGamalPublicKey is
    present on the issuance.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CONFIDENTIAL_CONVERT_BACK,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        # Validate blinding_factor length (should be 32 bytes = 64 hex chars)
        if len(self.blinding_factor) != BLINDING_FACTOR_LENGTH:
            errors["blinding_factor"] = (
                "blinding_factor must be 32 bytes (64 hex characters)"
            )

        # Validate MPTAmount is not zero
        if hasattr(self, "mpt_amount") and self.mpt_amount == 0:
            errors["mpt_amount"] = "mpt_amount cannot be zero"

        return errors
