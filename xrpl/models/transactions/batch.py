"""Model for Batch transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from typing_extensions import Self

from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Signer, Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


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
    tx_ids: Optional[List[str]] = None
    batch_signers: Optional[List[BatchSigner]] = None

    transaction_type: TransactionType = field(
        default=TransactionType.BATCH,
        init=False,
    )

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
