"""Model for ConfidentialClawback transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.confidential_convert import EQUALITY_PROOF_LENGTH
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class ConfidentialClawback(Transaction):
    """
    Represents a ConfidentialClawback transaction.

    Clawback involves the issuer forcibly reclaiming funds from a holder's
    account. This action is fundamentally incompatible with standard confidential
    transfers, as the issuer does not possess the holder's private ElGamal key
    and therefore cannot generate the required ZKPs for a normal ConfidentialSend.
    To solve this, the protocol introduces a single and privileged transaction
    that allows an issuer to verifiably reclaim funds in one uninterruptible step.

    This issuer-only transaction is designed to convert a holder's entire
    confidential balance directly into the issuer's public reserve.
    """

    account: str = REQUIRED  # type: ignore
    """The Issuer account sending the transaction."""

    holder: str = REQUIRED  # type: ignore
    """The account from which funds are being clawed back."""

    mptoken_issuance_id: str = REQUIRED  # type: ignore
    """The unique identifier for the MPT issuance."""

    mpt_amount: int = REQUIRED  # type: ignore
    """The plaintext total amount being removed."""

    zk_proof: str = REQUIRED  # type: ignore
    """An Equality Proof validating the amount."""

    transaction_type: TransactionType = field(
        default=TransactionType.CONFIDENTIAL_CLAWBACK,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if hasattr(self, "account") and hasattr(self, "holder"):
            if self.account == self.holder:
                errors["holder"] = "Cannot claw back from the same account"

        if len(self.zk_proof) != EQUALITY_PROOF_LENGTH:
            errors["zk_proof"] = (
                "zk_proof must be 98 bytes (196 hex characters) for Equality Proof"
            )

        if hasattr(self, "mpt_amount") and self.mpt_amount == 0:
            errors["mpt_amount"] = "mpt_amount cannot be zero"

        return errors
