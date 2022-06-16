"""Types used by the parser."""

from typing import List, Literal

from typing_extensions import TypedDict


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
    """A currency amunt model. Has the same fields as `Balance`"""

    pass


class OfferChange(TypedDict):
    """A single offer change."""

    direction: Literal["buy", "sell"]
    quantity: CurrencyAmount
    total_price: CurrencyAmount
    sequence: int
    status: Literal["created", "partially-filled", "filled", "cancelled"]
    maker_exchange_rate: str
    expiration_time: int


class AccountOfferChange(TypedDict):
    """A model representing an account's offer change."""

    account: str
    offer_change: OfferChange


class AccountOfferChanges(TypedDict):
    """A model representing an account's offer changes."""

    account: str
    offer_changes: List[OfferChange]
