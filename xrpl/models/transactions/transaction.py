"""TODO: docstring"""

from abc import ABC
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class Transaction(ABC):
    """
    TODO: docstring
    https://xrpl.org/transaction-types.html
    https://xrpl.org/transaction-common-fields.html
    """

    account: str
    transaction_type: str
    fee: str
    sequence: int
    account_transaction_id: Optional[str] = None
    flags: Optional[int] = None
    last_ledger_sequence: Optional[int] = None
    memos: Optional[List[Any]] = None
    signers: Optional[List[Any]] = None
    source_tag: Optional[int] = None
    signing_public_key: Optional[str] = None
    transaction_signature: Optional[str] = None
