"""Model for EscrowCreate transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from typing import Dict, Optional

from cryptoconditions import PreimageSha256  # type: ignore
from typing_extensions import Self, TypedDict

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class EscrowCreate(Transaction):
    """
    Represents an `EscrowCreate <https://xrpl.org/escrowcreate.html>`_
    transaction, which locks up XRP until a specific time or condition is met.
    """

    amount: Amount = REQUIRED  # type: ignore
    """
    Amount of XRP, in drops, to deduct from the sender's balance and set
    aside in escrow. This field is required.

    :meta hide-value:
    """

    destination: str = REQUIRED  # type: ignore
    """
    The address that should receive the escrowed XRP when the time or
    condition is met. This field is required.

    :meta hide-value:
    """

    destination_tag: Optional[int] = None
    """
    An arbitrary `destination tag
    <https://xrpl.org/source-and-destination-tags.html>`_ that
    identifies the reason for the Escrow, or a hosted recipient to pay.
    """

    cancel_after: Optional[int] = None
    """
    The time, in seconds since the Ripple Epoch, when this escrow expires.
    This value is immutable; the funds can only be returned the sender after
    this time.
    """

    finish_after: Optional[int] = None
    """
    The time, in seconds since the Ripple Epoch, when the escrowed XRP can
    be released to the recipient. This value is immutable; the funds cannot
    move until this time is reached.
    """

    condition: Optional[str] = None
    """
    Hex value representing a `PREIMAGE-SHA-256 crypto-condition
    <https://tools.ietf.org/html/draft-thomas-crypto-conditions-04#section-8.1.>`_
    The funds can only be delivered to the recipient if this condition is
    fulfilled.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.ESCROW_CREATE,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        if (
            self.cancel_after is not None
            and self.finish_after is not None
            and self.finish_after >= self.cancel_after
        ):
            errors["EscrowCreate"] = (
                "The finish_after time must be before the cancel_after time."
            )

        return errors


class CryptoConditions(TypedDict):
    """
    A typed-dictionary containing the condition and the fulfillment for
    conditional Escrows
    """

    condition: str
    fulfillment: str


def generate_escrow_cryptoconditions(secret: bytes) -> CryptoConditions:
    """Generate a condition and fulfillment for escrows

    Args:
        secret: Cryptographic source of randomness used to generate the condition and
            fulfillment

    Returns:
        A pair of condition and fulfillment is returned

    """
    fufill = PreimageSha256(preimage=secret)
    cond_fulfillment: CryptoConditions = {
        "condition": str.upper(fufill.condition_binary.hex()),
        "fulfillment": str.upper(fufill.serialize_binary().hex()),
    }
    return cond_fulfillment
    # return {
    #     "condition": str.upper(fufill.condition_binary.hex()),
    #     "fulfillment": str.upper(fufill.serialize_binary().hex()),
    # }
