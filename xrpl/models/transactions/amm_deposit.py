"""Model for AMMDeposit transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.amounts import Amount, IssuedCurrencyAmount
from xrpl.models.currencies.currency import Currency
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMDeposit(Transaction):
    """
    AMMDeposit is the deposit transaction used to add liquidity to the AMM instance
    pool, thus obtaining some share of the instance's pools in the form of LPToken.

    The following are the recommended valid combinations:
    - LPToken
    - Amount
    - Amount and Amount2
    - Amount and LPToken
    - Amount and EPrice
    """

    asset: Currency = REQUIRED  # type: ignore
    """
    Specifies one of the pool assets (XRP or token) of the AMM instance.
    """

    asset2: Currency = REQUIRED  # type: ignore
    """
    Specifies the other pool asset of the AMM instance.
    """

    lp_token: Optional[IssuedCurrencyAmount] = None
    """
    Specifies the amount of shares of the AMM instance pools that the trader
    wants to redeem or trade in.
    """

    amount: Optional[Amount] = None
    """
    Specifies one of the pool assets (XRP or token) of the AMM instance to
    deposit more of its value.
    """

    amount2: Optional[Amount] = None
    """
    Specifies the other pool asset of the AMM instance to deposit more of its
    value.
    """

    e_price: Optional[Amount] = None
    """
    Specifies the maximum effective-price that LPToken can be traded out.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_DEPOSIT,
        init=False,
    )

    def _get_errors(self: AMMDeposit) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.amount2 is not None and self.amount is None:
            errors["AMMDeposit"] = "Must set `amount` with `amount2`"
        elif self.e_price is not None and self.amount is None:
            errors["AMMDeposit"] = "Must set `amount` with `e_price`"
        elif self.lp_token is None and self.amount is None:
            errors["AMMDeposit"] = "Must set at least `lp_token` or `amount`"
        return errors
