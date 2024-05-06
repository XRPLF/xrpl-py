"""Model for OracleDelete transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OracleDelete(Transaction):
    """Represents an OracleDelete transaction."""

    account: str = REQUIRED  # type: ignore
    """Account is the account that has the Oracle update and delete privileges.
    This field corresponds to the Owner field on the PriceOracle ledger object."""

    oracle_document_id: int = REQUIRED  # type: ignore
    """OracleDocumentID is a unique identifier of the Price Oracle for the given
    Account."""

    transaction_type: TransactionType = field(
        default=TransactionType.ORACLE_DELETE,
        init=False,
    )
