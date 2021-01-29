"""TODO: docstrings"""

from __future__ import annotations

from typing import Any, Dict, List

from xrpl.addresscodec import is_valid_xaddress, xaddress_to_classic_address
from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.binary_wrappers.binary_serializer import BinarySerializer
from xrpl.binary_codec.definitions.field_instance import FieldInstance
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.serialized_type import SerializedType

OBJECT_END_MARKER_BYTE = bytes([0xE1])
OBJECT_END_MARKER = "ObjectEndMarker"
SERIALIZED_OBJECT = "SerializedObject"
DESTINATION = "Destination"
ACCOUNT = "Account"
SOURCE_TAG = "SourceTag"
DEST_TAG = "DestinationTag"


def handle_xaddress(field: str, xaddress: str) -> Dict[str, Any]:
    """TODO: docstring"""
    (classic_address, tag, is_test_network) = xaddress_to_classic_address(xaddress)
    if field == DESTINATION:
        tag_name = DEST_TAG
    elif field == ACCOUNT:
        tag_name = SOURCE_TAG
    elif tag is not None:
        raise XRPLBinaryCodecException("{} cannot have an associated tag".format(field))

    if tag is not None:
        return {field: classic_address, tag_name: tag}
    return {field: classic_address}


class SerializedObject(SerializedType):
    """TODO: docstrings"""

    def from_parser(parser: BinaryParser) -> SerializedObject:
        """TODO: docstrings"""
        serializer = BinarySerializer()

        while not parser.is_end():
            field = parser.read_field()
            if field.name == OBJECT_END_MARKER:
                break

            associated_value = parser.read_field_value(field)
            serializer.write_field_and_value(field, associated_value)
            if field.type.name == SERIALIZED_OBJECT:
                serializer.put(OBJECT_END_MARKER_BYTE)

        return SerializedObject(serializer.to_bytes())

    def from_value(value: Dict[str, Any]) -> SerializedObject:
        """TODO: docstring"""
        serializer = BinarySerializer()

        x_address_decoded = {}
        for (k, v) in value.items():
            if is_valid_xaddress(v):
                handled = handle_xaddress(k, v)
                if handled[SOURCE_TAG] is not None and value[SOURCE_TAG] is not None:
                    raise XRPLBinaryCodecException(
                        "Cannot have Account X-Address and SourceTag"
                    )
                if handled[DEST_TAG] is not None and value[DEST_TAG] is not None:
                    raise XRPLBinaryCodecException(
                        "Cannot have Destination X-Address and DestinationTag"
                    )
            x_address_decoded[k] = v

        sorted_keys: List[FieldInstance] = []
        for f in x_address_decoded:
            # TODO: somehow convert f to a FieldInstance???
            if (
                f is not None
                and x_address_decoded[f.name] is not None
                and f.is_serialized
            ):
                sorted_keys.append(f)
        sorted_keys.sort(lambda x: x.ordinal)

        for field in sorted_keys:
            serializer.write_field_and_value(field, x_address_decoded[field.name])
            if field.type.name == SERIALIZED_OBJECT:
                serializer.put(OBJECT_END_MARKER_BYTE)

        return SerializedObject(serializer.to_bytes())

    def to_json(self) -> Dict[str, Any]:
        """TODO: docstring"""
        parser = BinaryParser(self.to_string())
        accumulator = {}

        while not parser.is_end():
            field = parser.read_field()
            if field.name == OBJECT_END_MARKER:
                break
            accumulator[field.name] = parser.read_field_value(field).to_json()

        return accumulator
