"""TODO: docstring"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from xrpl.models.exceptions import XrplModelException
from xrpl.models.issued_currency import IssuedCurrency


@dataclass(frozen=True)
class OfferCreateTransaction:
    """
    Represents an OfferCreate transaction on the XRP Ledger.
    An OfferCreate transaction is effectively a limit order.
    It defines an intent to exchange currencies, and creates
    an Offer object if not completely fulfilled when placed.
    Offers can be partially fulfilled.

    See https://xrpl.org/offercreate.html.
    """

    taker_gets: Union[str, IssuedCurrency]
    taker_pays: Union[str, IssuedCurrency]
    expiration: Optional[int] = None
    offer_sequence: Optional[int] = None

    def __init__(
        self: OfferCreateTransaction,
        taker_gets: Union[str, IssuedCurrency],
        taker_pays: Union[str, IssuedCurrency],
        expiration: Optional[int] = None,
        offer_sequence: Optional[int] = None,
        flags: int = 0,
    ):
        """TODO: docstring"""
        self.taker_gets = taker_gets
        self.taker_pays = taker_pays
        self.expiration = expiration
        self.offer_sequence = offer_sequence

    @classmethod
    def from_value(
        cls: OfferCreateTransaction, value: Dict[str, Any]
    ) -> OfferCreateTransaction:
        """TODO: docstring"""
        assert "taker_gets" in value
        assert "taker_pays" in value

        if isinstance(value["taker_gets"], str):
            taker_gets = value["taker_gets"]
        elif isinstance(value["taker_gets"], dict):
            taker_gets = IssuedCurrency.from_value(value["taker_gets"])
        else:
            raise XrplModelException(
                "Cannot convert `taker_gets` value into `str` or `IssuedCurrency`"
            )

        if isinstance(value["taker_pays"], str):
            taker_pays = value["taker_pays"]
        elif isinstance(value["taker_pays"], dict):
            taker_pays = IssuedCurrency.from_value(value["taker_pays"])
        else:
            raise XrplModelException(
                "Cannot convert `taker_pays` value into `str` or `IssuedCurrency`"
            )

        expiration = None
        if "expiration" in value:
            assert isinstance(
                value["expiration"], int
            ), "`expiration` value is not an integer"
            expiration = value["expiration"]

        offer_sequence = None
        if "offer_sequence" in value:
            assert isinstance(
                value["offer_sequence"], int
            ), "`offer_sequence` value is not an integer"
            offer_sequence = value["offer_sequence"]

        return OfferCreateTransaction(
            taker_gets=taker_gets,
            taker_pays=taker_pays,
            expiration=expiration,
            offer_sequence=offer_sequence,
        )

    def to_json(self) -> Dict[str, Any]:
        """TODO: docstring"""
        return_dict = {"taker_gets": self.taker_gets, "taker_pays": self.taker_pays}
        if self.expiration is not None:
            return_dict["expiration"] = self.expiration
        if self.offer_sequence is not None:
            return_dict["offer_sequence"] = self.offer_sequence

        return return_dict
