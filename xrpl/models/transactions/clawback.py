"""Model for Clawback transaction type and related flags."""
from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Clawback(Transaction):
    """The clawback transaction claws back issued funds from token holders."""

    amount: IssuedCurrencyAmount = REQUIRED  # type: ignore
    """
    The amount of currency to deliver. If the Partial Payment flag is set,
    deliver *up to* this amount instead. This field is required.

    :meta hide-value:
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CLAWBACK,
        init=False,
    )
