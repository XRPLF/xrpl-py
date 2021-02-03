"""Class for serializing/deserializing transactions."""

from __future__ import annotations

from typing import Any, Dict, List

from typing_extensions import Final

from xrpl.addresscodec import is_valid_xaddress, xaddress_to_classic_address
from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.definitions.definitions import get_field_instance
from xrpl.binary_codec.definitions.field_instance import FieldInstance
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.serialized_type import SerializedType

_OBJECT_END_MARKER_BYTE: Final = bytes([0xE1])
_OBJECT_END_MARKER: Final = "ObjectEndMarker"
_SERIALIZED_TRANSACTION: Final = "SerializedTransaction"
_DESTINATION: Final = "Destination"
_ACCOUNT: Final = "Account"
_SOURCE_TAG: Final = "SourceTag"
_DEST_TAG: Final = "DestinationTag"


def handle_xaddress(field: str, xaddress: str) -> Dict[str, str]:
    """Break down an X-Address into a classic address and a tag.

    Args:
        field: Name of field
        xaddress: X-Address corresponding to the field

    Returns:
        A dictionary representing the classic address and tag.

    Raises:
        XRPLBinaryCodecException: field-tag combo is invalid.
    """
    (classic_address, tag, is_test_network) = xaddress_to_classic_address(xaddress)
    if field == _DESTINATION:
        tag_name = _DEST_TAG
    elif field == _ACCOUNT:
        tag_name = _SOURCE_TAG
    elif tag is not None:
        raise XRPLBinaryCodecException("{} cannot have an associated tag".format(field))

    if tag is not None:
        return {field: classic_address, tag_name: tag}
    return {field: classic_address}


class SerializedTransaction(SerializedType):
    """Class for serializing/deserializing transactions."""

    @classmethod
    def from_parser(
        cls: SerializedTransaction, parser: BinaryParser
    ) -> SerializedTransaction:
        """
        Construct a SerializedTransaction from a BinaryParser.

        Args:
            parser: The parser to construct a SerializedTransaction from.

        Returns:
            The SerializedTransaction constructed from parser.
        """
        from xrpl.binary_codec.binary_wrappers.binary_serializer import BinarySerializer

        serializer = BinarySerializer()

        while not parser.is_end():
            field = parser.read_field()
            if field.name == _OBJECT_END_MARKER:
                break

            associated_value = parser.read_field_value(field)
            serializer.write_field_and_value(field, associated_value)
            if field.type == _SERIALIZED_TRANSACTION:
                serializer.put(_OBJECT_END_MARKER_BYTE)

        return SerializedTransaction(serializer.to_bytes())

    @classmethod
    def from_value(
        cls: SerializedTransaction, value: Dict[str, Any]
    ) -> SerializedTransaction:
        """
        Create a SerializedTransaction object from a dictionary.

        Args:
            value: The dictionary to construct a SerializedTransaction from.

        Returns:
            The SerializedTransaction object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the SerializedTransaction can't be constructed
                from value.
        """
        from xrpl.binary_codec.binary_wrappers.binary_serializer import BinarySerializer

        serializer = BinarySerializer()

        xaddress_decoded = {}
        for (k, v) in value.items():
            if isinstance(v, str) and is_valid_xaddress(v):
                handled = handle_xaddress(k, v)
                if handled[_SOURCE_TAG] is not None and value[_SOURCE_TAG] is not None:
                    raise XRPLBinaryCodecException(
                        "Cannot have Account X-Address and SourceTag"
                    )
                if handled[_DEST_TAG] is not None and value[_DEST_TAG] is not None:
                    raise XRPLBinaryCodecException(
                        "Cannot have Destination X-Address and DestinationTag"
                    )
                xaddress_decoded.update(handled)
            else:
                xaddress_decoded[k] = v

        sorted_keys: List[FieldInstance] = []
        for field_name in xaddress_decoded:
            field_instance = get_field_instance(field_name)
            if (
                field_instance is not None
                and xaddress_decoded[field_instance.name] is not None
                and field_instance.is_serialized
            ):
                sorted_keys.append(field_instance)
        sorted_keys.sort(key=lambda x: x.ordinal)

        for field in sorted_keys:
            associated_value = field.associated_type.from_value(
                xaddress_decoded[field.name]
            )
            serializer.write_field_and_value(field, associated_value)
            if field.type == _SERIALIZED_TRANSACTION:
                serializer.put(_OBJECT_END_MARKER_BYTE)

        return SerializedTransaction(serializer.to_bytes())

    def to_json(self: SerializedTransaction) -> Dict[str, Any]:
        """
        Returns the JSON representation of a SerializedTransaction.

        Returns:
            The JSON representation of a SerializedTransaction.
        """
        parser = BinaryParser(self.to_string())
        accumulator = {}

        while not parser.is_end():
            field = parser.read_field()
            if field.name == _OBJECT_END_MARKER:
                break
            accumulator[field.name] = parser.read_field_value(field).to_json()

        return accumulator
