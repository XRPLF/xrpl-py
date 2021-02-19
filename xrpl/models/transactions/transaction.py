"""
The base class for all transaction types. Represents fields common to all transaction
types.

See https://xrpl.org/transaction-types.html.
See https://xrpl.org/transaction-common-fields.html.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from typing_extensions import Final

from xrpl.models.base_model import BaseModel

REQUIRED: Final[object] = object()


class TransactionType(str, Enum):
    """Enum containing the different Transaction types."""

    AccountSet = "AccountSet"
    OfferCancel = "OfferCancel"
    OfferCreate = "OfferCreate"
    SetRegularKey = "SetRegularKey"


@dataclass(frozen=True)
class Transaction(BaseModel):
    """
    The base class for all transaction types. Represents fields common to all
    transaction types.

    See https://xrpl.org/transaction-types.html.
    See https://xrpl.org/transaction-common-fields.html.
    """

    account: str = REQUIRED
    fee: str = REQUIRED
    sequence: int = REQUIRED
    account_txn_id: Optional[str] = None
    flags: Optional[int] = None
    last_ledger_sequence: Optional[int] = None
    # TODO make type
    memos: Optional[List[Any]] = None
    # TODO make type
    signers: Optional[List[Any]] = None
    source_tag: Optional[int] = None
    signing_pub_key: Optional[str] = None
    txn_signature: Optional[str] = None

    def _get_errors(self: Transaction) -> Dict[str, str]:
        return {
            attr: f"{attr} is not set"
            for attr, value in self.__dict__.items()
            if value is REQUIRED
        }
