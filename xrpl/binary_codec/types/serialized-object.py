"""TODO: docstrings"""

from __future__ import annotations

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.binary_wrappers.binary_serializer import BinarySerializer
from xrpl.binary_codec.types.serialized_type import SerializedType

OBJECT_END_MARKER_BYTE = bytes([0xE1])
OBJECT_END_MARKER = "ObjectEndMarker"
ST_OBJECT = "STObject"
DESTINATION = "Destination"
ACCOUNT = "Account"
SOURCE_TAG = "SourceTag"
DEST_TAG = "DestinationTag"


class SerializedObject(SerializedType):
    """TODO: docstrings"""

    def from_parser(parser: BinaryParser) -> SerializedObject:
        """TODO: docstrings"""
        lst = []
        serializer = BinarySerializer(lst)

        while not parser.is_end():
            field = parser.read_field()
            if field.name == OBJECT_END_MARKER:
                break

            associated_value = parser.read_field_value(field)

            serializer.write_field_and_value(field, associated_value)
