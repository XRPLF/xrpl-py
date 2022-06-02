from __future__ import annotations

from typing import Any, Dict, Optional, Type, Union

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.core.binarycodec.types.currency import Currency
from xrpl.core.binarycodec.types.serialized_type import SerializedType
from xrpl.models.currencies import IssuedCurrency as IssuedCurrencyModel


class IssuedCurrency(SerializedType):
    def __init__(self: IssuedCurrency, buffer: bytes) -> None:
        """Construct an IssuedCurrency from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_value(
        cls: Type[IssuedCurrency], value: Union[str, Dict[str, str]]
    ) -> IssuedCurrency:
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
        currency = Currency.from_parser(parser)
        if currency.to_json() == "XRP":
            return cls(bytes(currency))

        issuer = parser.read(20)
        return cls(bytes(currency) + issuer)

    def to_json(self: IssuedCurrency) -> Union[str, Dict[Any, Any]]:
        parser = BinaryParser(str(self))
        currency = Currency.from_parser(parser)
        if currency.to_json() == "XRP":
            return currency.to_json()

        issuer = AccountID.from_parser(parser)
        return {"currency": currency.to_json(), "issuer": issuer.to_json()}
