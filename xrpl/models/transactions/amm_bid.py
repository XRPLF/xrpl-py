"""Model for AMMBid transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from typing_extensions import Final

from xrpl.models.amounts import Amount
from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init

_MAX_AUTH_ACCOUNTS: Final[int] = 4


@require_kwargs_on_init
@dataclass(frozen=True)
class AuthAccount(BaseModel):
    """Represents one entry in a list of AuthAccounts used in AMMBid transaction."""

    Account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    @classmethod
    def is_dict_of_model(cls: Type[AuthAccount], dictionary: Dict[str, Any]) -> bool:
        """
        Returns True if the input dictionary was derived by the `to_dict`
        method of an instance of this class. In other words, True if this is
        a dictionary representation of an instance of this class.

        NOTE: does not account for model inheritance, IE will only return True
        if dictionary represents an instance of this class, but not if
        dictionary represents an instance of a subclass of this class.

        Args:
            dictionary: The dictionary to check.

        Returns:
            True if dictionary is a dict representation of an instance of this
            class.
        """
        return (
            isinstance(dictionary, dict)
            and "auth_account" in dictionary
            and super().is_dict_of_model(dictionary["auth_account"])
        )

    @classmethod
    def from_dict(cls: Type[AuthAccount], value: Dict[str, Any]) -> AuthAccount:
        """
        Construct a new AuthAccount from a dictionary of parameters.

        Args:
            value: The value to construct the AuthAccount from.

        Returns:
            A new AuthAccount object, constructed using the given parameters.
        """
        if len(value) == 1 and "auth_account" in value:
            return super(AuthAccount, cls).from_dict(value["auth_account"])
        return super(AuthAccount, cls).from_dict(value)

    def to_dict(self: AuthAccount) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a AuthAccount.

        Returns:
            The dictionary representation of a AuthAccount.
        """
        return {"auth_account": super().to_dict()}


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMBid(Transaction):
    """
    AMMBid is used to place a bid for the auction slot of obtaining trading advantages
    of an AMM instance.

    An AMM instance auctions off the trading advantages to users (arbitrageurs) at a
    discounted TradingFee for a 24 hour slot.
    """

    amm_id: str = REQUIRED  # type: ignore
    """
    A hash that uniquely identifies the AMM instance. This field is required.
    """

    min_slot_price: Optional[Amount] = None
    """
    This field represents the minimum price that the bidder wants to pay for the slot.
    It is specified in units of LPToken. If specified let MinSlotPrice be X and let
    the slot-price computed by price scheduling algorithm be Y, then bidder always pays
    the max(X, Y).
    """

    max_slot_price: Optional[Amount] = None
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
