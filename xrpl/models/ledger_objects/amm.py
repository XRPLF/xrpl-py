"""Models for the Ledger Object `AMM`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.auth_account import AuthAccount
from xrpl.models.base_model import BaseModel
from xrpl.models.currencies import Currency
from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMM(LedgerObject):
    """The model for the `AMM` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    """
    The address of the special account that holds this AMM's assets.
    This field is required.
    """

    asset: Currency = REQUIRED  # type: ignore
    """
    The definition for one of the two assets this AMM holds. This field is required.
    """

    asset2: Currency = REQUIRED  # type: ignore
    """
    The definition for the other asset this AMM holds. This field is required.
    """

    auction_slot: Optional[AuctionSlot] = None
    """
    Details of the current owner of the auction slot, as an Auction Slot object.
    """

    lptoken_balance: IssuedCurrencyAmount = REQUIRED  # type: ignore
    """
    The total outstanding balance of liquidity provider tokens from this AMM instance.
    The holders of these tokens can vote on the AMM's trading fee in proportion to
    their holdings, or redeem the tokens for a share of the AMM's assets which grows
    with the trading fees collected. This field is required.
    """

    trading_fee: int = REQUIRED  # type: ignore
    """
    The percentage fee to be charged for trades against this AMM instance, in units
    of 1/100,000. The maximum value is 1000, for a 1% fee. This field is required.
    """

    vote_slots: Optional[List[VoteEntry]] = None
    """
    A list of vote objects, representing votes on the pool's trading fee.
    """

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the sender's owner directory links to this entry,
    in case the directory consists of multiple pages.
    """

    flags: int = 0  # type: ignore
    """
    A bit-map of boolean flags. No flags are defined for the AMM object
    type, so this value is always 0. This field is required.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.AMM,
        init=False,
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class AuctionSlot(BaseModel):
    """
    The model for the `AuctionSlot` object
    Details of the current owner of the auction slot.
    """

    account: str = REQUIRED  # type: ignore
    """
    The current owner of this auction slot. This field is required.
    """

    auth_accounts: Optional[List[AuthAccount]] = None
    """
    A list of at most 4 additional accounts that are authorized to trade at the
    discounted fee for this AMM instance.
    """

    discounted_fee: int = REQUIRED  # type: ignore
    """
    The trading fee to be charged to the auction owner, in the same format as
    TradingFee.
    By default this is 0, meaning that the auction owner can trade at no fee instead of
    the standard fee for this AMM. This field is required.
    """

    expiration: int = REQUIRED  # type: ignore
    """
    The time when this slot expires, in seconds since the Ripple Epoch.
    This field is required.
    """

    price: IssuedCurrencyAmount = REQUIRED  # type: ignore
    """
    The amount the auction owner paid to win this slot, in LP Tokens.
    This field is required.
    """


@require_kwargs_on_init
@dataclass(frozen=True)
class VoteEntry(NestedModel):
    """A model for the `VoteEntry` object"""

    account: str = REQUIRED  # type: ignore
    """
    The account that cast the vote. This field is required.
    """

    trading_fee: int = REQUIRED  # type: ignore
    """
    The proposed trading fee, in units of 1/100,000; a value of 1 is equivalent
    to 0.001%. The maximum value is 1000, indicating a 1% fee. This field is required.
    """

    vote_weight: int = REQUIRED  # type: ignore
    """
    The weight of the vote, in units of 1/100,000. For example, a value of 1234 means
    this vote counts as 1.234% of the weighted total vote. The weight is determined by
    the percentage of this AMM's LP Tokens the account owns. The maximum value is
    100000. This field is required.
    """
