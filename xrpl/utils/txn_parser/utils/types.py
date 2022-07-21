"""Types used by the parser."""

from typing import List

from typing_extensions import Literal, TypedDict


class OptionalIssuer(TypedDict, total=False):
    """The optional issuer field for an account's balance."""

    """
    The `issuer` field is separated from `Balance` to make it
    optional, while keeping `currency` and `value` required.
    """
    issuer: str
    """The issuer of the currency. This value is optional."""


class Balance(OptionalIssuer):
    """A account's balance model."""

    currency: str
    """The currency code."""
    value: str
    """The amount of the currency."""


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


class OptionalExpiration(TypedDict, total=False):
    """The optional expiration field for an offer."""

    """
    The `Expiration` field is separated from `OfferChange` to make it
    optional, while keeping all other fields required.
    """

    expiration_time: int


class OfferChange(OptionalExpiration):
    """A single offer change."""

    flags: int
    taker_gets: CurrencyAmount
    taker_pays: CurrencyAmount
    sequence: int
    status: Literal["created", "partially-filled", "filled", "cancelled"]
    maker_exchange_rate: str


class AccountOfferChange(TypedDict):
    """A model representing an account's offer change."""

    maker_account: str
    offer_change: OfferChange


class AccountOfferChanges(TypedDict):
    """A model representing an account's offer changes."""

    maker_account: str
    offer_changes: List[OfferChange]
