"""
Represents an OfferCreate transaction on the XRP Ledger. An OfferCreate transaction is
effectively a limit order. It defines an intent to exchange currencies, and creates an
Offer object if not completely fulfilled when placed. Offers can be partially fulfilled.

See https://xrpl.org/offercreate.html.
"""
from __future__ import annotations  # Requires Python 3.7+

from typing import Any, List, Optional

from xrpl.models.amount import Amount
from xrpl.models.transactions.transaction import Transaction


class OfferCreateTransaction(Transaction):
    """
    Represents an OfferCreate transaction on the XRP Ledger. An OfferCreate transaction
    is effectively a limit order. It defines an intent to exchange currencies, and
    creates an Offer object if not completely fulfilled when placed. Offers can be
    partially fulfilled.

    See https://xrpl.org/offercreate.html.
    """

    def __init__(
        self: OfferCreateTransaction,
        *,  # forces remaining params to be named, not just listed
        account: str,
        fee: str,
        sequence: int,
        taker_gets: Amount,
        taker_pays: Amount,
        expiration: Optional[int] = None,
        offer_sequence: Optional[int] = None,
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
        self.taker_gets = taker_gets
        self.taker_pays = taker_pays
        self.expiration = expiration
        self.offer_sequence = offer_sequence

        super().__init__(
            account=account,
            transaction_type=TransactionType.OfferCreate,
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
