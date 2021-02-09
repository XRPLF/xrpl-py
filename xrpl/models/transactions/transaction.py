"""TODO: docstring"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Transaction(ABC):
    """
    TODO: docstring
    https://xrpl.org/transaction-types.html
    https://xrpl.org/transaction-common-fields.html
    """

    def __init__(
        self,
        *,
        account: str,
        transaction_type: str,
        fee: str,
        sequence: int,
        account_transaction_id: Optional[str] = None,
        flags: Optional[int] = None,
        last_ledger_sequence: Optional[int] = None,
        memos: Optional[List[Any]] = None,
        signers: Optional[List[Any]] = None,
        source_tag: Optional[int] = None,
        signing_public_key: Optional[str] = None,
        transaction_signature: Optional[str] = None,
    ):
        """TODO: docstring"""
        self.account = account
        self.transaction_type = transaction_type
        self.fee = fee
        self.sequence = sequence
        self.account_transaction_id = account_transaction_id
        self.flags = flags
        self.last_ledger_sequence = last_ledger_sequence
        self.memos = memos
        self.signers = signers
        self.source_tag = source_tag
        self.signing_public_key = signing_public_key
        self.transaction_signature = transaction_signature

    @classmethod
    @abstractmethod
    def from_dict(cls: Transaction, value: Dict[str, Any]) -> Transaction:
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

    @abstractmethod
    def to_json(self: Transaction) -> Dict[str, Any]:
        """TODO: docstring"""
        raise NotImplementedError("Transaction.to_json not implemented.")

    def _get_transaction_json(self: Transaction) -> Dict[str, Any]:
        """TODO: docstring"""
        return_dict = {
            "account": self.account,
            "transaction_type": self.transaction_type,
            "fee": self.fee,
            "sequence": self.sequence,
        }
        if self.account_transaction_id is not None:
            return_dict["account_transaction_id"] = self.account_transaction_id
        if self.flags is not None:
            return_dict["flags"] = self.flags
        if self.last_ledger_sequence is not None:
            return_dict["last_ledger_sequence"] = self.last_ledger_sequence
        if self.memos is not None:
            return_dict["memos"] = self.memos
        if self.signers is not None:
            return_dict["signers"] = self.signers
        if self.source_tag is not None:
            return_dict["source_tag"] = self.source_tag
        if self.signing_public_key is not None:
            return_dict["signing_public_key"] = self.signing_public_key
        if self.transaction_signature is not None:
            return_dict["transaction_signature"] = self.transaction_signature
        return return_dict

    def __eq__(self: Transaction, other: object) -> bool:
        """TODO: docstring"""
        if not isinstance(other, Transaction):
            return False
        return self.to_json() == other.to_json()

    def __repr__(self):
        """TODO: docstring"""
        repr_items = []
        for key, value in self.to_json():
            repr_items.append(f"{key}={repr(value)}")
        return "{}({})".format(type(self).__name, ", ".join(repr_items))
