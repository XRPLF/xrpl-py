"""TODO: docstring"""

from __future__ import annotations

from typing import Any, Dict, List

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.account_id import AccountID
from xrpl.binary_codec.types.currency import Currency
from xrpl.binary_codec.types.serialized_type import SerializedType

TYPE_ACCOUNT = 0x01
TYPE_CURRENCY = 0x10
TYPE_ISSUER = 0x20

PATHSET_END_BYTE = 0x00
PATH_SEPARATOR_BYTE = 0xFF


class Hop(SerializedType):
    """TODO: docstring"""

    @classmethod
    def from_value(value: Dict[str, Any]) -> Hop:
        """TODO: docstring"""
        data_type = bytes(0)
        buffer = b""
        if "account" in value:
            account_id = AccountID.from_value(value["account"])
            buffer += account_id.buffer
            data_type |= TYPE_ACCOUNT
        if "currency" in value:
            currency = Currency.from_value()
            buffer += currency.buffer
            data_type |= TYPE_CURRENCY
        if "issuer" in value:
            issuer = AccountID.from_value(value["issuer"])
            buffer += issuer.buffer
            data_type |= TYPE_ISSUER

        return Hop(data_type + buffer)

    @classmethod
    def from_parser(parser: BinaryParser) -> Hop:
        """TODO: docstring"""
        data_type = parser.read_uint8()
        buffer = bytes(data_type)

        if data_type & TYPE_ACCOUNT:
            account_id = parser.read(AccountID.WIDTH)
            buffer += account_id
        if data_type & TYPE_CURRENCY:
            currency = parser.read(Currency.WIDTH)
            buffer += currency
        if data_type & TYPE_ISSUER:
            issuer = parser.read(AccountID.WIDTH)
            buffer += issuer

        return Hop(buffer)

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

    def to_bytes(self):
        """TODO: docstring"""
        return self.buffer

    @property
    def type(self):
        """TODO: docstring"""
        return self.buffer[0]


class Path(SerializedType):
    """Class for serializing/deserializing Paths"""

    @classmethod
    def from_value(cls, value: List[Dict[str, Any]]) -> Path:
        """TODO: docstring"""
        buffer: bytes = b""
        for hop_dict in value:
            hop = Hop.from_value(hop_dict)
            buffer += hop.to_bytes()
        return Path(buffer)

    @classmethod
    def from_parser(parser: BinaryParser) -> Path:
        """TODO: docstring"""
        buffer: List[bytes] = []
        while not parser.end():
            hop = Hop.from_parser(parser)
            buffer.append(hop.to_bytes)

            if (
                parser.peek() == PATHSET_END_BYTE
                or parser.peek() == PATH_SEPARATOR_BYTE
            ):
                break

        return Path(buffer)

    def to_json(self) -> List[Dict[str, Any]]:
        """TODO: docstring"""
        json = []
        path_parser = BinaryParser(self.buffer.hex())

        while not path_parser.end():
            hop = Hop.from_parser(path_parser)
            json.append(hop.to_json())

        return json
