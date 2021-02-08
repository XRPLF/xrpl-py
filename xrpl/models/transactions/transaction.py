"""TODO: docstring"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


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

    @abstractmethod
    @classmethod
    def from_value(self: Transaction, value: Dict[str, Any]) -> Transaction:
        """
        Construct a new Transaction from a literal value.

        Args:
            value: The value to construct the Transaction from.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("Transaction.from_value not implemented.")

    def is_signed(self) -> bool:
        """TODO: docstring"""
        return (
            self.signing_public_key is not None
            and self.transaction_signature is not None
        )
