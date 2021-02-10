"""Base object for ledger objects on XRPL"""
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum


class LedgerObjectType(str, Enum):
    """Enum containing the different LedgerObject types."""

    AccountRoot = "AccountRoot"


@dataclass(frozen=True)
class LedgerObject(ABC):
    """
    Base object for ledger objects on XRPL.

    Attributes:
        type: The type of the LedgerObject.
    """

    type: LedgerObjectType = field(init=False)
