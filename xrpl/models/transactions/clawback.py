"""Model for Clawback transaction type and related flags."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from xrpl.models.amounts import IssuedCurrencyAmount, is_issued_currency, is_xrp
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
    The amount of currency to claw back. The issuer field is used for the token holder's
    address, from whom the tokens will be clawed back.

    :meta hide-value:
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CLAWBACK,
        init=False,
    )

    def _get_errors(self: Clawback) -> Dict[str, str]:
        errors = super()._get_errors()

        # Amount transaction errors
        if is_xrp(self.amount):
            errors["amount"] = "``amount`` cannot be XRP."

        if is_issued_currency(self.amount):
            if self.account == self.amount.issuer:
                errors["amount"] = "Holder's address is wrong."

        return errors
