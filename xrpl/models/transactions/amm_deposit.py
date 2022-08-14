"""Model for AMMDeposit transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMDeposit(Transaction):
    """
    AMDeposit is the deposit transaction used to add liquidity to the AMM instance pool,
    thus obtaining some share of the instance's pools in the form of LPTokens.

    The following are the recommended valid combinations:
    - LPTokens
    - Asset1In
    - Asset1In and Asset2In
    - Asset1In and LPTokens
    - Asset1In and EPrice
    """

    amm_hash: str = REQUIRED  # type: ignore
    """
    AMMHash is a hash that uniquely identifies the AMM instance.
    """

    lptokens: Optional[Amount] = None
    """
    LPTokens specifies the amount of shares of the AMM instance pools that the trader
    wants to redeem or trade in.
    """

    asset1_in: Optional[Amount] = None
    """
    Asset1In specifies one of the pool assets (XRP or token) of the AMM instance to
    deposit more of its value.
    """

    asset2_in: Optional[Amount] = None
    """
    Asset2 specifies the other pool asset of the AMM instance to deposit more of its
    value.
    """

    e_price: Optional[Amount] = None
    """
    EPrice specifies the maximum effective-price that LPTokens can be traded out.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_DEPOSIT,
        init=False,
    )

    def _get_errors(self: AMMDeposit) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.lptokens is None and self.asset1_in is None:
            errors["AMMDeposit"] = "Must set either or both `lptokens` and `asset1_in`"
        elif self.asset2_in is not None and self.asset1_in is None:
            errors["AMMDeposit"] = "Must set `asset1_in` with `asset2_in`"
        elif self.e_price is not None and self.asset1_in is None:
            errors["AMMDeposit"] = "Must set `asset1_in` with `e_price`"
        return errors
