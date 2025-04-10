"""Model for AMMDeposit transaction type."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.amm_deposit_flag import AMMDepositFlag
from xrpl.models.currency import Currency
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMDeposit(Transaction):
    """
    Deposit funds into an Automated Market Maker (AMM) instance and receive the AMM's
    liquidity provider tokens (LP Tokens) in exchange. You can deposit one or both of the
    assets in the AMM's pool.  If successful, this transaction creates a trust line to the
    AMM Account (limit 0) to hold the LP Tokens.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_DEPOSIT, init=False
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
    (Optional) The amount of one asset to deposit to the AMM. If present, this must match
    the type of one of the assets (tokens or XRP) in the AMM's pool.
    """

    amount2: Optional[Any] = None
    """
    (Optional) The amount of another asset to add to the AMM. If present, this must match
    the type of the other asset in the AMM's pool and cannot be the same asset as Amount.
    """

    e_price: Optional[Any] = None
    """
    (Optional) The maximum effective price, in the deposit asset, to pay for each LP Token
    received.
    """

    lp_token_out: Optional[Any] = None
    """
    (Optional) How many of the AMM's LP Tokens to buy.
    """

    trading_fee: Optional[int] = None
    """
    (Optional) Submit a vote for the AMM's trading fee, in units of 1/100,000; a value of 1
    is equivalent to 0.001%. The maximum value is 1000, indicating a 1% fee.
    """

    def _get_errors(self: AMMDeposit) -> Dict[str, str]:
        errors = super._get_errors()
        if self.amount2 is not None and self.amount is None:
            errors["AMMDeposit"] = "Must set `amount` with `amount2.`"
        if self.e_price is not None and self.amount is None:
            errors["AMMDeposit"] = "Must set `amount` with `e_price.`"
        if self.lp_token_out is None and self.amount is None:
            errors["AMMDeposit"] = (
                "At least one of `lp_token_out`, `amount` must be set."
            )
        if self.trading_fee is not None and self.trading_fee < 0:
            errors["AMMDeposit"] = (
                "Field `trading_fee` must have a value greater than or equal to 0"
            )
        if self.trading_fee is not None and self.trading_fee > 1000:
            errors["AMMDeposit"] = (
                "Field `trading_fee` must have a value less than or equal to 1000"
            )
        return errors


class AMMDepositFlagInterface(FlagInterface):
    """
    Enum for AMMDeposit Transaction Flags.
    """

    TF_LP_TOKEN: bool
    TF_TWO_ASSET: bool
    TF_TWO_ASSET_IF_EMPTY: bool
    TF_SINGLE_ASSET: bool
    TF_ONE_ASSET_LP_TOKEN: bool
    TF_LIMIT_LP_TOKEN: bool


class AMMDepositFlag(int, Enum):
    """
    Enum for AMMDeposit Transaction Flags.
    """

    TF_LP_TOKEN = 0x00010000
    """
    Deposit both of this AMM&#39;s assets, in amounts calculated so that you receive the specified amount of LP Tokens in return. The amounts deposited maintain the relative proportions of the two assets the AMM already holds.
    """

    TF_TWO_ASSET = 0x00100000
    """
    Deposit both of this AMM&#39;s assets, up to the specified amounts. The actual amounts deposited must maintain the same balance of assets as the AMM already holds, so the amount of either one deposited MAY be less than specified. The amount of LP Tokens you get in return is based on the total value deposited.
    """

    TF_TWO_ASSET_IF_EMPTY = 0x00800000
    """
    Deposit both of this AMM&#39;s assets, in exactly the specified amounts, to an AMM with an empty asset pool. The amount of LP Tokens you get in return is based on the total value deposited.
    """

    TF_SINGLE_ASSET = 0x00080000
    """
    Deposit exactly the specified amount of one asset, and receive an amount of LP Tokens based on the resulting share of the pool (minus fees).
    """

    TF_ONE_ASSET_LP_TOKEN = 0x00200000
    """
    Deposit up to the specified amount of one asset, so that you receive exactly the specified amount of LP Tokens in return (after fees).
    """

    TF_LIMIT_LP_TOKEN = 0x00400000
    """
    Deposit up to the specified amount of one asset, but pay no more than the specified effective price per LP Token (after fees).
    """
