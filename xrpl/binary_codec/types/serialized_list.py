"""Class for serializing and deserializing Lists of objects."""

from __future__ import annotations

from typing import Any, List

from typing_extensions import Final

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.serialized_dict import SerializedDict
from xrpl.binary_codec.types.serialized_type import SerializedType

_ARRAY_END_MARKER: Final = bytes([0xF1])
_ARRAY_END_MARKER_NAME: Final = "ArrayEndMarker"

_OBJECT_END_MARKER: Final = bytes([0xE1])


class SerializedList(SerializedType):
    """Class for serializing and deserializing Lists of objects."""

    @classmethod
    def from_parser(cls: SerializedList, parser: BinaryParser) -> SerializedList:
        """
        Construct a SerializedList from a BinaryParser.

        Args:
            parser: The parser to construct a SerializedList from.

        Returns:
            The SerializedList constructed from parser.
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
        return SerializedList(bytestring)

    @classmethod
    def from_value(cls: SerializedList, value: List[Any]) -> SerializedList:
        """
        Create a SerializedList object from a dictionary.

        Args:
            value: The dictionary to construct a SerializedList from.

        Returns:
            The SerializedList object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the provided value isn't a list or contains
                non-dict elements.
        """
        if not isinstance(value, list):
            raise XRPLBinaryCodecException(
                "Cannot construct SerializedList from a non-list object"
            )

        if len(value) > 0 and not isinstance(value[0], dict):
            raise XRPLBinaryCodecException(
                ("Cannot construct SerializedList from a list of non-dict" " objects")
            )

        bytestring = b""
        for obj in value:
            transaction = SerializedDict.from_value(obj)
            bytestring += transaction.to_bytes()
        bytestring += _ARRAY_END_MARKER
        return SerializedList(bytestring)

    def to_json(self: SerializedList) -> List[Any]:
        """
        Returns the JSON representation of a SerializedList.

        Returns:
            The JSON representation of a SerializedList.
        """
        result = []
        parser = BinaryParser(self.to_string())

        while not parser.is_end():
            field = parser.read_field()
            if field.name == _ARRAY_END_MARKER_NAME:
                break

            outer = {}
            outer[field.name] = SerializedDict.from_parser(parser).to_json()
            result.append(outer)
        return result
