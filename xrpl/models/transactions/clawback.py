"""Model for Clawback transaction type and related flags."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.flags import FlagInterface
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


class ClawbackFlag(int, Enum):
    """Transaction Flags for an Clawback Transaction."""

    TF_SET_FREEZE = 0x00100000
    """Freeze the trust line."""

    TF_CLEAR_FREEZE = 0x00200000
    """Unfreeze the trust line."""


class ClawbackFlagInterface(FlagInterface):
    """
    Transactions of the Clawback type support additional values in the Flags field.
    This TypedDict represents those options.
    """

    TF_SET_FREEZE: bool
    TF_CLEAR_FREEZE: bool


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
