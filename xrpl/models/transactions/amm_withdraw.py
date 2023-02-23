"""Model for AMMWithdraw transaction type."""
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


class AMMWithdrawFlag(int, Enum):
    """
    Transactions of the AMMWithdraw type support additional values in the Flags field.
    This enum represents those options.
    """

    TF_LP_TOKEN = 0x00010000
    TF_WITHDRAW_ALL = 0x00020000
    TF_ONE_ASSET_WITHDRAW_ALL = 0x00040000
    TF_SINGLE_ASSET = 0x00080000
    TF_TWO_ASSET = 0x00100000
    TF_ONE_ASSET_LP_TOKEN = 0x00200000
    TF_LIMIT_LP_TOKEN = 0x00400000


class AMMWithdrawFlagInterface(FlagInterface):
    """
    Transactions of the AMMWithdraw type support additional values in the Flags field.
    This TypedDict represents those options.
    """

    TF_LP_TOKEN: bool
    TF_WITHDRAW_ALL: bool
    TF_ONE_ASSET_WITHDRAW_ALL: bool
    TF_SINGLE_ASSET: bool
    TF_TWO_ASSET: bool
    TF_ONE_ASSET_LP_TOKEN: bool
    TF_LIMIT_LP_TOKEN: bool


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMWithdraw(Transaction):
    """
    AMMWithdraw is the withdraw transaction used to remove liquidity from the AMM
    instance pool, thus redeeming some share of the pools that one owns in the form
    of LPToken.

    The following are the recommended valid combinations:
    - LPTokenIn
    - Amount
    - Amount and Amount2
    - Amount and LPTokenIn
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

    lp_token_in: Optional[IssuedCurrencyAmount] = None
    """
    Specifies the amount of shares of the AMM instance pools that the trader
    wants to redeem or trade in.
    """

    amount: Optional[Amount] = None
    """
    Specifies one of the pools assets that the trader wants to remove.
    If the asset is XRP, then the Amount is a string specifying the number of drops.
    Otherwise it is an IssuedCurrencyAmount object.
    """

    amount2: Optional[Amount] = None
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
        if self.amount2 is not None and self.amount is None:
            errors["AMMWithdraw"] = "Must set `amount` with `amount2`"
        elif self.e_price is not None and self.amount is None:
            errors["AMMWithdraw"] = "Must set `amount` with `e_price`"
        return errors
