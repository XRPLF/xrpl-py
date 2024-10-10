"""Model for Batch transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

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
