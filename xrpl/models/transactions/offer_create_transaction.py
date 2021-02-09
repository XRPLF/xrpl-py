"""
Represents an OfferCreate transaction on the XRP Ledger. An OfferCreate transaction is
effectively a limit order. It defines an intent to exchange currencies, and creates an
Offer object if not completely fulfilled when placed. Offers can be partially fulfilled.

See https://xrpl.org/offercreate.html.
"""
from __future__ import annotations  # Requires Python 3.7+

from typing import Any, Dict, List, Optional, Union

from xrpl.models.issued_currency import IssuedCurrency
from xrpl.models.transactions.transaction import Transaction


def _currency_amount_to_json(
    amount: Union[str, IssuedCurrency]
) -> Union[Dict[str, Any], str]:
    if isinstance(amount, str):
        return amount
    return amount.to_json()


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
    ):
        """Construct an OfferCreateTransaction from the given parameters."""
        if isinstance(taker_gets, dict):
            self.taker_gets = IssuedCurrency.from_dict(taker_gets)
        else:
            self.taker_gets = taker_gets

        if isinstance(taker_pays, dict):
            self.taker_pays = IssuedCurrency.from_dict(taker_pays)
        else:
            self.taker_pays = taker_pays

        self.expiration = expiration
        self.offer_sequence = offer_sequence

        super().__init__(
            account=account,
            transaction_type="OfferCreate",
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

    @classmethod
    def from_dict(
        cls: OfferCreateTransaction, value: Dict[str, Any]
    ) -> OfferCreateTransaction:
        """
        Construct an OfferCreateTransaction from a dictionary of parameters.

        Args:
            value: The dictionary to construct an OfferCreateTransaction from.

        Returns:
            The OfferCreateTransaction constructed from value.
        """
        return OfferCreateTransaction(**value)

    def to_json(self) -> Dict[str, Any]:
        """
        Return the value of this OfferCreateTransaction encoded as a dictionary.

        Returns:
            The JSON representation of the OfferCreateTransaction.
        """
        return_dict = {
            "taker_gets": _currency_amount_to_json(self.taker_gets),
            "taker_pays": _currency_amount_to_json(self.taker_pays),
        }
        if self.expiration is not None:
            return_dict["expiration"] = self.expiration
        if self.offer_sequence is not None:
            return_dict["offer_sequence"] = self.offer_sequence

        return {**self._get_transaction_json(), **return_dict}
