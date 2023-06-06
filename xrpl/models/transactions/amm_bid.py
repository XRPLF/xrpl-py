"""Model for AMMBid transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Final

from xrpl.models.amounts import Amount
from xrpl.models.auth_account import AuthAccount
from xrpl.models.currencies import Currency
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init

_MAX_AUTH_ACCOUNTS: Final[int] = 4


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMBid(Transaction):
    """
    AMMBid is used to place a bid for the auction slot of obtaining trading advantages
    of an AMM instance.

    An AMM instance auctions off the trading advantages to users (arbitrageurs) at a
    discounted TradingFee for a 24 hour slot.
    """

    asset: Currency = REQUIRED  # type: ignore
    """
    Specifies one of the pool assets (XRP or token) of the AMM instance.
    """

    asset2: Currency = REQUIRED  # type: ignore
    """
    Specifies the other pool asset of the AMM instance.
    """

    bid_min: Optional[Amount] = None
    """
    This field represents the minimum price that the bidder wants to pay for the slot.
    It is specified in units of LPToken. If specified let MinSlotPrice be X and let
    the slot-price computed by price scheduling algorithm be Y, then bidder always pays
    the max(X, Y).
    """

    bid_max: Optional[Amount] = None
    """
    This field represents the maximum price that the bidder wants to pay for the slot.
    It is specified in units of LPToken.
    """

    auth_accounts: Optional[List[AuthAccount]] = None
    """
    This field represents an array of XRPL account IDs that are authorized to trade
    at the discounted fee against the AMM instance.
    A maximum of four accounts can be provided.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_BID,
        init=False,
    )

    def _get_errors(self: AMMBid) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "auth_accounts": self._get_auth_accounts_error(),
            }.items()
            if value is not None
        }

    def _get_auth_accounts_error(self: AMMBid) -> Optional[str]:
        if (
            self.auth_accounts is not None
            and len(self.auth_accounts) > _MAX_AUTH_ACCOUNTS
        ):
            return f"Length must not be greater than {_MAX_AUTH_ACCOUNTS}"
        return None
