"""Types used by the parser."""

from typing import List, Union

from typing_extensions import Literal, NotRequired, TypedDict


class Balance(TypedDict):
    """A account's balance model."""

    currency: str
    """The currency code."""

    value: str
    """The amount of the currency."""

    issuer: NotRequired[str]
    """The issuer of the currency. This value is optional."""


class AccountBalance(TypedDict):
    """A single account balance."""

    account: str
    """The affected account."""
    balance: Balance
    """The balance."""


class AccountBalances(TypedDict):
    """A model representing an account's balances."""

    account: str
    balances: List[Balance]


class CurrencyAmount(Balance):
    """A currency amount model. Has the same fields as `Balance`"""

    pass


class MPTCurrencyAmount(TypedDict):
    """An MPT amount model, in the same shape as an MPT amount in the ledger."""

    mpt_issuance_id: str
    """The MPTokenIssuanceID of the MPT."""

    value: str
    """The amount of the MPT, in its smallest unit."""


class OfferChange(TypedDict):
    """A single offer change."""

    flags: int
    taker_gets: Union[CurrencyAmount, MPTCurrencyAmount]
    taker_pays: Union[CurrencyAmount, MPTCurrencyAmount]
    sequence: int
    status: Literal["created", "partially-filled", "filled", "cancelled"]
    maker_exchange_rate: str
    expiration_time: NotRequired[int]


class AccountOfferChange(TypedDict):
    """A model representing an account's offer change."""

    maker_account: str
    offer_change: OfferChange


class AccountOfferChanges(TypedDict):
    """A model representing an account's offer changes."""

    maker_account: str
    offer_changes: List[OfferChange]
