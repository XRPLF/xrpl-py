"""Model for AMMWithdraw transaction type."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.amm_withdraw_flag import AMMWithdrawFlag
from xrpl.models.currency import Currency
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMWithdraw(Transaction):
    """
    Withdraw assets from an Automated Market Maker (AMM) instance by returning the AMM's
    liquidity provider tokens (LP Tokens).
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_WITHDRAW, init=False
    )

    asset: Currency = REQUIRED
    """
    (Required) The definition for one of the assets in the AMM's pool. In JSON, this is an
                object with currency and issuer fields (omit issuer for XRP).
    """

    asset2: Currency = REQUIRED
    """
    (Required) The definition for the other asset in the AMM's pool. In JSON, this is an
                object with currency and issuer fields (omit issuer for XRP).
    """

    amount: Optional[Any] = None
    """
    (Optional) The amount of one asset to withdraw from the AMM. This must match the type of
    one of the assets (tokens or XRP) in the AMM's pool.
    """

    amount2: Optional[Any] = None
    """
    (Optional) The amount of another asset to withdraw from the AMM. If present, this must
    match the type of the other asset in the AMM's pool and cannot be the same type as
    Amount.
    """

    e_price: Optional[Any] = None
    """
    (Optional) The minimum effective price, in LP Token returned, to pay per unit of the
    asset to withdraw.
    """

    lp_token_in: Optional[Any] = None
    """
    (Optional) How many of the AMM's LP Tokens to redeem.
    """

    def _get_errors(self: AMMWithdraw) -> Dict[str, str]:
        errors = super._get_errors()
        if self.amount2 is not None and self.amount is None:
            errors["AMMWithdraw"] = "Must set `amount` with `amount2.`"
        if self.e_price is not None and self.amount is None:
            errors["AMMWithdraw"] = "Must set `amount` with `e_price.`"
        return errors


class AMMWithdrawFlagInterface(FlagInterface):
    """
    Enum for AMMWithdraw Transaction Flags.
    """

    TF_LP_TOKEN: bool
    TF_WITHDRAW_ALL: bool
    TF_ONE_ASSET_WITHDRAW_ALL: bool
    TF_SINGLE_ASSET: bool
    TF_TWO_ASSET: bool
    TF_ONE_ASSET_LP_TOKEN: bool
    TF_LIMIT_LP_TOKEN: bool


class AMMWithdrawFlag(int, Enum):
    """
    Enum for AMMWithdraw Transaction Flags.
    """

    TF_LP_TOKEN = 0x00010000
    """
    Perform a double-asset withdrawal and receive the specified amount of LP Tokens.
    """

    TF_WITHDRAW_ALL = 0x00020000
    """
    Perform a double-asset withdrawal returning all your LP Tokens.
    """

    TF_ONE_ASSET_WITHDRAW_ALL = 0x00040000
    """
    Perform a single-asset withdrawal returning all of your LP Tokens.
    """

    TF_SINGLE_ASSET = 0x00080000
    """
    Perform a single-asset withdrawal with a specified amount of the asset to withdraw.
    """

    TF_TWO_ASSET = 0x00100000
    """
    Perform a double-asset withdrawal with specified amounts of both assets.
    """

    TF_ONE_ASSET_LP_TOKEN = 0x00200000
    """
    Perform a single-asset withdrawal and receive the specified amount of LP Tokens.
    """

    TF_LIMIT_LP_TOKEN = 0x00400000
    """
    Perform a single-asset withdrawal with a specified effective price.
    """
