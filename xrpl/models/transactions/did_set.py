"""Model for DIDSet transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DIDSet(Transaction):
    """Represents a DIDSet transaction."""

    attestation: Optional[str] = None
    did_document: Optional[str] = None
    uri: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.DID_SET,
        init=False,
    )
