"""Model for AMMWithdraw transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.amounts import Amount, IssuedCurrencyAmount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMWithdraw(Transaction):
    """
    AMMWithdraw is the withdraw transaction used to remove liquidity from the AMM
    instance pool, thus redeeming some share of the pools that one owns in the form
    of LPToken.

    The following are the recommended valid combinations:
    - LPToken
    - Asset1Out
    - Asset1Out and Asset2Out
    - Asset1Out and LPToken
    - Asset1Out and EPrice
    """

    amm_id: str = REQUIRED  # type: ignore
    """
    A hash that uniquely identifies the AMM instance. This field is required.
    """

    lp_token: Optional[IssuedCurrencyAmount] = None
    """
    Specifies the amount of shares of the AMM instance pools that the trader
    wants to redeem or trade in.
    """

    asset1_out: Optional[Amount] = None
    """
    Specifies one of the pools assets that the trader wants to remove.
    If the asset is XRP, then the Asset1Out is a string specifying the number of drops.
    Otherwise it is an IssuedCurrencyAmount object.
    """

    asset2_out: Optional[Amount] = None
    """
    Specifies the other pool asset that the trader wants to remove.
    """

    e_price: Optional[Amount] = None
    """
    Specifies the effective-price of the token out after successful execution of
    the transaction.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_WITHDRAW,
        init=False,
    )

    def _get_errors(self: AMMWithdraw) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.asset2_out is not None and self.asset1_out is None:
            errors["AMMWithdraw"] = "Must set `asset1_out` with `asset2_out`"
        elif self.e_price is not None and self.asset1_out is None:
            errors["AMMWithdraw"] = "Must set `asset1_out` with `e_price`"
        elif self.lp_token is None and self.asset1_out is None:
            errors["AMMWithdraw"] = "Must set at least `lp_token` or `asset1_out`"
        return errors
