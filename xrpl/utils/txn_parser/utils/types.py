"""Types used by the parser."""

from typing import List, Optional

from typing_extensions import TypedDict


class BalanceType(TypedDict):
    """A account's balance model."""

    currency: str
    issuer: Optional[str]
    value: str


class BalanceChangeType(TypedDict):
    """A single balance change."""

    account: str
    """The affected account."""
    balance: BalanceType
    """The balance change."""


class BalanceChangesType(TypedDict):
    """A model representing an account's balance changes."""

    account: str
    balances: List[BalanceChangeType]
