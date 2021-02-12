"""
Represents an OfferCreate transaction on the XRP Ledger. An OfferCreate transaction is
effectively a limit order. It defines an intent to exchange currencies, and creates an
Offer object if not completely fulfilled when placed. Offers can be partially fulfilled.

See https://xrpl.org/offercreate.html.
"""
from __future__ import annotations  # Requires Python 3.7+

from typing import Any, Dict, List, Optional, Union

from xrpl.models.issued_currency import IssuedCurrency
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import (
    currency_amount_to_json_object,
    json_object_to_currency_amount,
)


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
        taker_gets: Union[str, IssuedCurrency, Dict[str, Any]],
        taker_pays: Union[str, IssuedCurrency, Dict[str, Any]],
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
        self.taker_gets = json_object_to_currency_amount(taker_gets)
        self.taker_pays = json_object_to_currency_amount(taker_pays)
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

    def to_json_object(self: OfferCreateTransaction) -> Dict[str, Any]:
        """
        Return the value of this OfferCreateTransaction encoded as a dictionary.

        Returns:
            The dictionary representation of the OfferCreateTransaction.
        """
        return {
            **super().to_json_object(),
            "taker_gets": currency_amount_to_json_object(self.taker_gets),
            "taker_pays": currency_amount_to_json_object(self.taker_pays),
        }
