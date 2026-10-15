"""Model for ConfidentialMPTClawback transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.confidential_mpt_constants import (
    CLAWBACK_PROOF_LENGTH,
    address_is_issuer,
    get_mpt_amount_error,
    get_mptoken_issuance_id_error,
)
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType


@dataclass(frozen=True, kw_only=True)
class ConfidentialMPTClawback(Transaction):
    """
    Represents a ConfidentialMPTClawback transaction.

    Clawback involves the issuer forcibly reclaiming funds from a holder's
    account. This action is fundamentally incompatible with standard confidential
    transfers, as the issuer does not possess the holder's private ElGamal key
    and therefore cannot generate the required ZKPs for a normal ConfidentialSend.
    To solve this, the protocol introduces a single and privileged transaction
    that allows an issuer to verifiably reclaim funds in one uninterruptible step.

    This issuer-only transaction is designed to convert a holder's entire
    confidential balance directly into the issuer's public reserve.
    """

    account: str = REQUIRED
    """The Issuer account sending the transaction."""

    holder: str = REQUIRED
    """The account from which funds are being clawed back."""

    mptoken_issuance_id: str = REQUIRED
    """The unique identifier for the MPT issuance."""

    mpt_amount: int = REQUIRED
    """The plaintext total amount being removed."""

    zk_proof: str = REQUIRED
    """An Equality Proof validating the amount."""

    transaction_type: TransactionType = field(
        default=TransactionType.CONFIDENTIAL_CLAWBACK,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        # Guard against the REQUIRED sentinel so super()'s "is not set" error
        # surfaces first instead of a TypeError on the sentinel.
        if (
            self.account is not REQUIRED
            and self.holder is not REQUIRED
            and self.account == self.holder
        ):
            errors["holder"] = "Cannot claw back from the same account"

        if (
            self.zk_proof is not REQUIRED
            and len(self.zk_proof) != CLAWBACK_PROOF_LENGTH
        ):
            errors["zk_proof"] = (
                "zk_proof must be 64 bytes (128 hex characters) for compact sigma proof"
            )

        if self.mpt_amount is not REQUIRED:
            amount_error = get_mpt_amount_error(self.mpt_amount, allow_zero=False)
            if amount_error is not None:
                errors["mpt_amount"] = amount_error

        if self.mptoken_issuance_id is not REQUIRED:
            issuance_id_error = get_mptoken_issuance_id_error(self.mptoken_issuance_id)
            if issuance_id_error is not None:
                errors["mptoken_issuance_id"] = issuance_id_error
            elif self.account is not REQUIRED and not address_is_issuer(
                self.mptoken_issuance_id, self.account
            ):
                # Clawback is issuer-only: Account MUST be the issuance's issuer
                # (temMALFORMED, ConfidentialMPTClawback.cpp preflight).
                errors["account"] = (
                    "ConfidentialMPTClawback account must be the issuance's issuer"
                )

        return errors
