"""Base object for ledger objects on XRPL"""
from dataclasses import dataclass, field
from enum import Enum

from xrpl.models.base_model import BaseModel


class LedgerObjectType(str, Enum):
    """Enum containing the different LedgerObject types."""

    AccountRoot = "AccountRoot"


@dataclass(frozen=True)
class LedgerObject(BaseModel):
    """
    Base object for ledger objects on the XRPL.

    Attributes:
        type: The type of the LedgerObject.
    """

    type: LedgerObjectType = field(init=False)
