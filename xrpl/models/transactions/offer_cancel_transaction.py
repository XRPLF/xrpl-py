"""
Represents an OfferCancel transaction on the XRP Ledger.

An OfferCancel transaction removes an Offer object from the XRP Ledger.

See https://xrpl.org/offercancel.html.
"""
from __future__ import annotations  # Requires Python 3.7+

from typing import Any, List, Optional

from xrpl.models.transactions.transaction import Transaction, TransactionType


class OfferCancelTransaction(Transaction):
    """
    Represents an OfferCancel transaction on the XRP Ledger.

    An OfferCancel transaction removes an Offer object from the XRP Ledger.

    See https://xrpl.org/offercancel.html.
    """

    def __init__(
        self: OfferCancelTransaction,
        *,  # forces remaining params to be named, not just listed
        account: str,
        fee: str,
        sequence: int,
        offer_sequence: int,
        account_transaction_id: Optional[str] = None,
        flags: Optional[int] = None,
        last_ledger_sequence: Optional[int] = None,
        memos: Optional[List[Any]] = None,
        signers: Optional[List[Any]] = None,
        source_tag: Optional[int] = None,
        signing_public_key: Optional[str] = None,
        transaction_signature: Optional[str] = None,
    ) -> None:
        """Construct an OfferCancelTransaction from the given parameters."""
        self.offer_sequence = offer_sequence

        super().__init__(
            account=account,
            transaction_type=TransactionType.OfferCancel,
            fee=fee,
            sequence=sequence,
            account_transaction_id=account_transaction_id,
            flags=flags,
            last_ledger_sequence=last_ledger_sequence,
            memos=memos,
            signers=signers,
            source_tag=source_tag,
            signing_public_key=signing_public_key,
            transaction_signature=transaction_signature,
        )
