"""Context manager and helpers for the serialization of a JSON object into bytes."""

from xrpl.binary_codec.definitions.field_instance import FieldInstance
from xrpl.binary_codec.types.serialized_type import SerializedType

# Constants used in length prefix encoding:
# max length that can be represented in a single byte per XRPL serialization encoding
MAX_SINGLE_BYTE_LENGTH = 192
# max length that can be represented in 2 bytes per XRPL serialization encoding
MAX_DOUBLE_BYTE_LENGTH = 12481
# max value that can be used in the second byte of a length field
MAX_SECOND_BYTE_VALUE = 240
# maximum length that can be encoded in a length prefix per XRPL serialization encoding
MAX_LENGTH_VALUE = 918744


def _encode_variable_length_prefix(length: int) -> bytes:
    """
    Helper function for length-prefixed fields including Blob types
    and some AccountID types. Calculates the prefix of variable length bytes.

    The length of the prefix is 1-3 bytes depending on the length of the contents:
    Content length <= 192 bytes: prefix is 1 byte
    192 bytes < Content length <= 12480 bytes: prefix is 2 bytes
    12480 bytes < Content length <= 918744 bytes: prefix is 3 bytes

    `See Length Prefixing <https://xrpl.org/serialization.html#length-prefixing>`_
    """
    if length <= MAX_SINGLE_BYTE_LENGTH:
        return length.to_bytes(1, byteorder="big", signed=False)
    if length < MAX_DOUBLE_BYTE_LENGTH:
        length -= MAX_SINGLE_BYTE_LENGTH + 1
        byte1 = ((length >> 8) + (MAX_SINGLE_BYTE_LENGTH + 1)).to_bytes(
            1, byteorder="big", signed=False
        )
        byte2 = (length & 0xFF).to_bytes(1, byteorder="big", signed=False)
        return byte1 + byte2
    if length <= MAX_LENGTH_VALUE:
        length -= MAX_DOUBLE_BYTE_LENGTH
        byte1 = ((MAX_SECOND_BYTE_VALUE + 1) + (length >> 16)).to_bytes(
            1, byteorder="big", signed=False
        )
        byte2 = ((length >> 8) & 0xFF).to_bytes(1, byteorder="big", signed=False)
        byte3 = (length & 0xFF).to_bytes(1, byteorder="big", signed=False)
        return byte1 + byte2 + byte3

    raise ValueError(
        "VariableLength field must be <= {} bytes long".format(MAX_LENGTH_VALUE)
    )


class BinarySerializer:
    """Serializes JSON to XRPL binary format."""

    def __init__(self) -> None:
        """Construct a BinarySerializer."""
        self.bytesink = bytes()

    def put(self, bytes_object: bytes) -> None:
        """Write given bytes to this BinarySerializer's bytesink."""
        self.bytesink += bytes_object

    def to_bytes(self) -> bytes:
        """Get the bytes representation of a BinarySerializer."""
        return self.bytesink

    def write_length_encoded(self, value: SerializedType) -> None:
        """Write a variable length encoded value to the BinarySerializer."""
        byte_object = bytearray()
        value.to_byte_sink(byte_object)
        length_prefix = _encode_variable_length_prefix(len(value))
        self.bytesink += length_prefix
        self.bytesink += byte_object

    def write_field_and_value(
        self, field: FieldInstance, value: SerializedType
    ) -> None:
        """Write field and value to the buffer."""
        self.bytesink += field.header.to_bytes()

        if field.is_variable_length_encoded:
            self.write_length_encoded(value)
        else:
            self.bytesink += value.to_bytes()
