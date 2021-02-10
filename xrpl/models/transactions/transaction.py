"""
The base class for all transaction types.

See https://xrpl.org/transaction-types.html.
See https://xrpl.org/transaction-common-fields.html.
"""
from __future__ import annotations

from typing import Any, List, Optional

from xrpl.models.base_model import BaseModel


class Transaction(BaseModel):
    """
    The base class for all transaction types.

    See https://xrpl.org/transaction-types.html.
    See https://xrpl.org/transaction-common-fields.html.
    """

    def __init__(
        self: Transaction,
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
    ) -> None:
        """Construct an OfferCreateTransaction from the given parameters."""
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
