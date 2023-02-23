"""Model for AMMDeposit transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from xrpl.models.amounts import Amount, IssuedCurrencyAmount
from xrpl.models.currencies import Currency
from xrpl.models.flags import FlagInterface
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


class AMMDepositFlag(int, Enum):
    """
    Transactions of the AMMDeposit type support additional values in the Flags field.
    This enum represents those options.
    """

    TF_LP_TOKEN = 0x00010000
    TF_SINGLE_ASSET = 0x00080000
    TF_TWO_ASSET = 0x00100000
    TF_ONE_ASSET_LP_TOKEN = 0x00200000
    TF_LIMIT_LP_TOKEN = 0x00400000


class AMMDepositFlagInterface(FlagInterface):
    """
    Transactions of the AMMDeposit type support additional values in the Flags field.
    This TypedDict represents those options.
    """

    TF_LP_TOKEN: bool
    TF_SINGLE_ASSET: bool
    TF_TWO_ASSET: bool
    TF_ONE_ASSET_LP_TOKEN: bool
    TF_LIMIT_LP_TOKEN: bool


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMDeposit(Transaction):
    """
    AMMDeposit is the deposit transaction used to add liquidity to the AMM instance
    pool, thus obtaining some share of the instance's pools in the form of LPToken.

    The following are the recommended valid combinations:
    - LPTokenOut
    - Amount
    - Amount and Amount2
    - Amount and LPTokenOut
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

    lp_token_out: Optional[IssuedCurrencyAmount] = None
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
        elif self.lp_token_out is None and self.amount is None:
            errors["AMMDeposit"] = "Must set at least `lp_token_out` or `amount`"
        return errors
