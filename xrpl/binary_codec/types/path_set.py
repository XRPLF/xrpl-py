"""TODO: docstring"""

from __future__ import annotations

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.account_id import AccountID
from xrpl.binary_codec.types.currency import Currency
from xrpl.binary_codec.types.serialized_type import SerializedType

TYPE_ACCOUNT = 0x01
TYPE_CURRENCY = 0x10
TYPE_ISSUER = 0x20


class Hop(SerializedType):
    """TODO: docstring"""

    @classmethod
    def from_value(value) -> Hop:
        """TODO: docstring"""
        buffer = [bytes([0])]
        if "account" in value:
            account_id = AccountID.from_value(value["account"])
            buffer.append(account_id.buffer)
            buffer[0] |= TYPE_ACCOUNT
        if "currency" in value:
            currency = Currency.from_value()
            buffer.append(currency.buffer)
            buffer[0] |= TYPE_CURRENCY
        if "issuer" in value:
            issuer = AccountID.from_value(value["issuer"])
            buffer.append(issuer.buffer)
            buffer[0] |= TYPE_ISSUER

        return Hop(buffer)

    @classmethod
    def from_parser(parser: BinaryParser) -> Hop:
        """TODO: docstring"""
        data_type = parser.read_uint8()
        buffer = [bytes(data_type)]

        if data_type & TYPE_ACCOUNT:
            account_id = parser.read(AccountID.WIDTH)
            buffer.append(account_id)
        if data_type & TYPE_CURRENCY:
            currency = parser.read(Currency.WIDTH)
            buffer.append(currency)
        if data_type & TYPE_ISSUER:
            issuer = parser.read(AccountID.WIDTH)
            buffer.append(issuer)

    def to_json(self):
        """TODO: docstring"""
        parser = BinaryParser(self.buffer.hex())
        data_type = parser.read_uint8()

        if data_type & TYPE_ACCOUNT:
            account_id = parser.read(AccountID.WIDTH).to_json()
        if data_type & TYPE_CURRENCY:
            currency = parser.read(Currency.WIDTH).to_json()
        if data_type & TYPE_ISSUER:
            issuer = parser.read(AccountID.WIDTH).to_json()

        return {"account": account_id, "currency": currency, "issuer": issuer}

    @property
    def type(self):
        """TODO: docstring"""
        return self.buffer[0]
