"""Model for AMMBid transaction type."""

from dataclasses import dataclass, field
from typing import Any, List, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.auth_account import AuthAccount
from xrpl.models.currency import Currency
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMBid(Transaction):
    """
    Bid on an Automated Market Maker's (AMM's) auction slot. If you win, you can trade
    against the AMM  at a discounted fee until you are outbid or 24 hours have passed. If
    you are outbid before 24 hours have passed, you are refunded part of the cost of your
    bid based on how much time remains. If the  AMM's trading fee is zero, you can still
    bid, but the auction slot provides no benefit unless the  trading fee changes.  You bid
    using the AMM's LP Tokens; the amount of a winning bid is returned to the AMM,
    decreasing the outstanding balance of LP Tokens.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_BID, init=False
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

    bid_min: Optional[Any] = None
    """
    (Optional) Pay at least this amount for the slot. Setting this value higher makes it
    harder for others to outbid you. If omitted, pay the minimum necessary to win the bid.
    """

    bid_max: Optional[Any] = None
    """
    (Optional) Pay at most this amount for the slot. If the cost to win the bid is higher
    than this amount, the transaction fails. If omitted, pay as much as necessary to win the
    bid.
    """

    auth_accounts: Optional[List[AuthAccount]] = None
    """
    (Optional) A list of up to 4 additional accounts that you allow to trade at the
    discounted fee. This cannot include the address of the transaction sender. Each of these
    objects should be an Auth Account object.
    """

    def _get_errors(self: AMMBid) -> Dict[str, str]:
        errors = super._get_errors()
        if self.auth_accounts is not None and len(self.auth_accounts) > 4:
            errors["AMMBid"] = (
                "Field `auth_accounts` must have a length less than or equal to 4"
            )
        return errors
