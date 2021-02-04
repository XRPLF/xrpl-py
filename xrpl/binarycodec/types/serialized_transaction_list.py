"""Class for serializing and deserializing Lists of objects.
See `Array Fields <https://xrpl.org/serialization.html#array-fields>`_
"""

from __future__ import annotations

from typing import Any, List

from typing_extensions import Final

from xrpl.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.binarycodec.types.serialized_transaction import SerializedTransaction
from xrpl.binarycodec.types.serialized_type import SerializedType

_ARRAY_END_MARKER: Final = bytes([0xF1])
_ARRAY_END_MARKER_NAME: Final = "ArrayEndMarker"

_OBJECT_END_MARKER: Final = bytes([0xE1])


class SerializedTransactionList(SerializedType):
    """Class for serializing and deserializing Lists of objects.
    See `Array Fields <https://xrpl.org/serialization.html#array-fields>`_
    """

    @classmethod
    def from_parser(
        cls: SerializedTransactionList, parser: BinaryParser
    ) -> SerializedTransactionList:
        """
        Construct a SerializedTransactionList from a BinaryParser.

        Args:
            parser: The parser to construct a SerializedTransactionList from.

        Returns:
            The SerializedTransactionList constructed from parser.
        """
        bytestring = b""

        while not parser.is_end():
            field = parser.read_field()
            if field.name == _ARRAY_END_MARKER_NAME:
                break
            bytestring += field.header.to_bytes()
            bytestring += parser.read_field_value(field).to_bytes()
            bytestring += _OBJECT_END_MARKER

        bytestring += _ARRAY_END_MARKER
        return SerializedTransactionList(bytestring)

    @classmethod
    def from_value(
        cls: SerializedTransactionList, value: List[Any]
    ) -> SerializedTransactionList:
        """
        Create a SerializedTransactionList object from a dictionary.

        Args:
            value: The dictionary to construct a SerializedTransactionList from.

        Returns:
            The SerializedTransactionList object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the provided value isn't a list or contains
                non-dict elements.
        """
        if not isinstance(value, list):
            raise XRPLBinaryCodecException(
                "Cannot construct SerializedTransactionList from a non-list object"
            )

        if len(value) > 0 and not isinstance(value[0], dict):
            raise XRPLBinaryCodecException(
                (
                    "Cannot construct SerializedTransactionList from a list of non-dict"
                    " objects"
                )
            )

        bytestring = b""
        for obj in value:
            transaction = SerializedTransaction.from_value(obj)
            bytestring += transaction.to_bytes()
        bytestring += _ARRAY_END_MARKER
        return SerializedTransactionList(bytestring)

    def to_json(self: SerializedTransactionList) -> List[Any]:
        """
        Returns the JSON representation of a SerializedTransactionList.

        Returns:
            The JSON representation of a SerializedTransactionList.
        """
        result = []
        parser = BinaryParser(self.to_string())

        while not parser.is_end():
            field = parser.read_field()
            if field.name == _ARRAY_END_MARKER_NAME:
                break

            outer = {}
            outer[field.name] = SerializedTransaction.from_parser(parser).to_json()
            result.append(outer)
        return result
