"""TODO: docstring"""

from __future__ import annotations

from typing import Any, List

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.serialized_transaction import SerializedTransaction
from xrpl.binary_codec.types.serialized_type import SerializedType

ARRAY_END_MARKER = bytes([0xF1])
ARRAY_END_MARKER_NAME = "ArrayEndMarker"

OBJECT_END_MARKER = bytes([0xE1])


class SerializedTransactionList(SerializedType):
    """TODO: docstring"""

    @classmethod
    def from_parser(
        cls: SerializedTransactionList, parser: BinaryParser
    ) -> SerializedTransactionList:
        """TODO: docstring"""
        bytestring = b""

        while not parser.is_end():
            field = parser.read_field()
            if field.name == ARRAY_END_MARKER_NAME:
                break
            else:
                bytestring += field.header.to_bytes()
                bytestring += parser.read_field_value(field).to_bytes()
                bytestring += OBJECT_END_MARKER

        bytestring += ARRAY_END_MARKER
        return SerializedTransactionList(bytestring)

    @classmethod
    def from_value(
        cls: SerializedTransactionList, value: List[Any]
    ) -> SerializedTransactionList:
        """TODO: docstring"""
        if isinstance(value, list) and (len(value) == 0 or isinstance(value[0], dict)):
            bytestring = b""
            for obj in value:
                transaction = SerializedTransaction.from_value(obj)
                bytestring += transaction.to_bytes()
            bytestring += ARRAY_END_MARKER
            return SerializedTransactionList(bytestring)

        raise XRPLBinaryCodecException(
            "Cannot construct SerializedTransactionList from value given"
        )

    def to_json(self: SerializedTransactionList) -> List[Any]:
        """TODO: docstring"""
        result = []
        parser = BinaryParser(self.to_string())

        while not parser.is_end():
            field = parser.read_field()
            if field.name == ARRAY_END_MARKER_NAME:
                break

            outer = {}
            outer[field.name] = SerializedTransaction.from_parser(parser).to_json()
            result.append(outer)
        return result
