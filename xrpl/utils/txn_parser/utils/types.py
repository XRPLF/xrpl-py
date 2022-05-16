"""Types used by the parser."""

from typing import List, Optional

from typing_extensions import TypedDict


class Balance(TypedDict):
    """A account's balance model."""

    currency: str
    issuer: Optional[str]
    value: str


class BalanceChange(TypedDict):
    """A single balance change."""

    account: str
    """The affected account."""
    balance: Balance
    """The balance change."""


class BalanceChanges(TypedDict):
    """A model representing an account's balance changes."""

    account: str
    balances: List[Balance]
