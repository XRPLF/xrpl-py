"""Model for OracleDelete transaction type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OracleDelete(Transaction):
    transaction_type: TransactionType = field(
        default=TransactionType.ORACLE_DELETE, init=False
    )

    oracle_document_id: str = REQUIRED
    """
    A unique identifier of the price oracle for the Account.
    """
