"""Codec for serializing and deserializing issued currency fields."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type, Union

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.core.binarycodec.types.currency import Currency
from xrpl.core.binarycodec.types.serialized_type import SerializedType
from xrpl.models.currencies import IssuedCurrency as IssuedCurrencyModel


class IssuedCurrency(SerializedType):
    """Codec for serializing and deserializing issued currency fields."""

    def __init__(self: IssuedCurrency, buffer: bytes) -> None:
        """Construct an IssuedCurrency from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_value(
        cls: Type[IssuedCurrency], value: Union[str, Dict[str, str]]
    ) -> IssuedCurrency:
        """
        Construct an IssuedCurrency object from a string or dictionary representation
        of an issued currency.

        Args:
            value: The dictionary to construct an IssuedCurrency object from.

        Returns:
            An IssuedCurrency object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the IssuedCurrency representation is invalid.
        """
        if isinstance(value, str):
            if value != "XRP":
                raise XRPLBinaryCodecException(f"{value} is an illegal currency")
            return cls(bytes(Currency.from_value(value)))

        if IssuedCurrencyModel.is_dict_of_model(value):
            currency_bytes = bytes(Currency.from_value(value["currency"]))
            issuer_bytes = bytes(AccountID.from_value(value["issuer"]))
            return cls(currency_bytes + issuer_bytes)

        raise XRPLBinaryCodecException(
            "Invalid type to construct an IssuedCurrency: expected str or dict,"
            f" received {value.__class__.__name__}."
        )

    @classmethod
    def from_parser(
        cls: Type[IssuedCurrency],
        parser: BinaryParser,
        length_hint: Optional[int] = None,
    ) -> IssuedCurrency:
        """
        Construct an IssuedCurrency object from an existing BinaryParser.

        Args:
            parser: The parser to construct the IssuedCurrency object from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The IssuedCurrency object constructed from a parser.
        """
        currency = Currency.from_parser(parser)
        if currency.to_json() == "XRP":
            return cls(bytes(currency))

        issuer = parser.read(20)
        return cls(bytes(currency) + issuer)

    def to_json(self: IssuedCurrency) -> Union[str, Dict[Any, Any]]:
        """
        Returns the JSON representation of an issued currency.

        Returns:
            The JSON representation of an IssuedCurrency.
        """
        parser = BinaryParser(str(self))
        currency: Union[str, Dict[Any, Any]] = Currency.from_parser(parser).to_json()
        if currency == "XRP":
            return currency

        issuer = AccountID.from_parser(parser)
        return {"currency": currency, "issuer": issuer.to_json()}
