"""Model for Batch transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from typing_extensions import Self

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import (
    Signer,
    Transaction,
    TransactionFlag,
    TransactionFlagInterface,
)
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class BatchFlag(int, Enum):
    """
    Transactions of the Batch type support additional values in the Flags field.
    This enum represents those options.
    """

    TF_ALL_OR_NOTHING = 0x00010000

    TF_ONLY_ONE = 0x00020000

    TF_UNTIL_FAILURE = 0x00040000

    TF_INDEPENDENT = 0x00080000


class BatchFlagInterface(TransactionFlagInterface):
    """
    Transactions of the Batch type support additional values in the Flags field.
    This TypedDict represents those options.
    """

    TF_ALL_OR_NOTHING: bool
    TF_ONLY_ONE: bool
    TF_UNTIL_FAILURE: bool
    TF_INDEPENDENT: bool


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class BatchSigner(NestedModel):
    """Represents a Batch signer."""

    account: str = REQUIRED  # type: ignore

    signing_pub_key: Optional[str] = None

    txn_signature: Optional[str] = None

    signers: Optional[List[Signer]] = None


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Batch(Transaction):
    """Represents a Batch transaction."""

    raw_transactions: List[Transaction] = REQUIRED  # type: ignore
    batch_signers: Optional[List[BatchSigner]] = None

    transaction_type: TransactionType = field(
        default=TransactionType.BATCH,
        init=False,
    )

    def __post_init__(self: Self) -> None:
        """Called by dataclasses immediately after __init__."""
        new_raw_transactions = []
        for tx in self.raw_transactions:
            # Ensure that every inner transaction has the tfInnerBatchTxn flag set.
            # If it does not, set it.
            if tx.has_flag(TransactionFlag.TF_INNER_BATCH_TXN):
                new_raw_transactions.append(tx)
            else:
                tx_dict = tx.to_dict()
                if "flags" not in tx_dict:
                    tx_dict["flags"] = TransactionFlag.TF_INNER_BATCH_TXN
                elif isinstance(tx_dict["flags"], int):
                    tx_dict["flags"] |= TransactionFlag.TF_INNER_BATCH_TXN
                elif isinstance(tx_dict["flags"], dict):
                    tx_dict["flags"]["TF_INNER_BATCH_TXN"] = True
                elif isinstance(self.flags, list):
                    tx_dict["flags"].append(TransactionFlag.TF_INNER_BATCH_TXN)
                elif tx_dict["flags"] is None:
                    tx_dict["flags"] = TransactionFlag.TF_INNER_BATCH_TXN
                else:
                    raise XRPLModelException(
                        "Invalid `flags` type for raw transaction in Batch."
                    )
                new_raw_transactions.append(Transaction.from_dict(tx_dict))
        # This is done before dataclass locks in the frozen fields
        # This way of editing is a bit hacky, but it's the recommended method for
        # updating frozen fields in dataclasses
        # https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(self, "raw_transactions", new_raw_transactions)
        super().__post_init__()

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        for i in range(len(self.raw_transactions)):
            tx = self.raw_transactions[i]
            if not tx.has_flag(TransactionFlag.TF_INNER_BATCH_TXN):
                errors[f"raw_transactions[{i}]"] = (
                    "RawTransaction must have tfInnerBatchTxn flag set."
                )
        if len(self.raw_transactions) < 2:
            errors["raw_transactions"] = "Batch must contain at least 2 transactions."
        return errors

    @classmethod
    def from_dict(cls: Type[Self], value: Dict[str, Any]) -> Self:
        """
        Construct a new Batch from a dictionary of parameters.

        Args:
            value: The value to construct the Batch from.

        Returns:
            A new Batch object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        new_value = {**value}
        new_value["raw_transactions"] = [
            (
                tx["raw_transaction"]
                if isinstance(tx, dict) and "raw_transaction" in tx
                else tx
            )
            for tx in value["raw_transactions"]
        ]
        return super(Transaction, cls).from_dict(new_value)

    def to_dict(self: Self) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Batch.

        Returns:
            The dictionary representation of a Batch.
        """
        tx_dict = super().to_dict()
        tx_dict["raw_transactions"] = [
            {"raw_transaction": tx} for tx in tx_dict["raw_transactions"]
        ]
        return tx_dict
