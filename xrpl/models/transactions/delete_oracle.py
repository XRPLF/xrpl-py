"""Model for DeleteOracle transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DeleteOracle(Transaction):
    """Represents a DeleteOracle transaction."""

    account: str = REQUIRED  # type: ignore
    oracle_document_id: Union[int, str] = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.DELETE_ORACLE,
        init=False,
    )
