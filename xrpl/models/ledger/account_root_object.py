"""TEST"""
from dataclasses import dataclass

from xrpl.models.ledger.ledger_object import LedgerObject


@dataclass
class AccountRootObject(LedgerObject):
    """Test."""

    pass
