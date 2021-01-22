"""Context manager and helpers for the deserialization of bytes into JSON."""
from typing import Tuple

from xrpl.binary_codec.definitions import definitions
from xrpl.binary_codec.definitions.field_header import FieldHeader
from xrpl.binary_codec.definitions.field_instance import FieldInstance
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.serialized_type import SerializedType

# Constants used in length prefix decoding:
# Max length that can be represented in a single byte per XRPL serialization encoding
MAX_SINGLE_BYTE_LENGTH = 192
# Max length that can be represented in 2 bytes per XRPL serialization restrictions
MAX_DOUBLE_BYTE_LENGTH = 12481
# Max value that can be used in the second byte of a length field
MAX_SECOND_BYTE_VALUE = 240
# Max value that can be represented using one 8-bit byte (2^8)
MAX_BYTE_VALUE = 256
# Max value that can be represented in using two 8-bit bytes (2^16)
MAX_DOUBLE_BYTE_VALUE = 65536


class BinaryParser:
    """Deserializes from hex-encoded XRPL binary format to JSON fields and values."""

    def __init__(self, hex_bytes: str):
        """Construct a BinaryParser that will parse hex-encoded bytes."""
        self.bytes = bytes.fromhex(hex_bytes)

    def __len__(self):
        """Return the number of bytes in this parser's buffer."""
        return len(self.bytes)

    def peek(self) -> bytes:
        """Peek the first byte of the BinaryParser."""
        if len(self.bytes) > 0:
            return self.bytes[0]
        return None

    def skip(self, n):
        """Consume the first n bytes of the BinaryParser."""
        if n <= len(self.bytes):
            self.bytes = self.bytes[n:]
        raise XRPLBinaryCodecException(
            "BinaryParser can't skip {} bytes, only contains {}.".format(
                n, len(self.bytes)
            )
        )

    def read(self, n: int) -> bytes:
        """Consume and return the first n bytes of the BinaryParser."""
        if n <= len(self.bytes):
            first_n_bytes = self.bytes[:n]
            self.skip(n)
            return first_n_bytes
        raise XRPLBinaryCodecException(
            "BinaryParser can't read {} bytes, only contains {}.".format(
                n, len(self.bytes)
            )
        )

    def read_uint8(self) -> int:
        """Read 1 byte from parser and return as unsigned int."""
        return int.from_bytes(self.read(1), byteorder="big")

    def read_uint16(self) -> int:
        """Read 2 bytes from parser and return as unsigned int."""
        return int.from_bytes(self.read(2), byteorder="big")

    def read_uint32(self) -> int:
        """Read 4 bytes from parser and return as unsigned int."""
        return int.from_bytes(self.read(4), byteorder="big")

    def is_end(self, custom_end=None) -> bool:
        """TODO: I'm not sure what this actually does yet."""
        return len(self.bytes) == 0 or (
            custom_end is not None and len(self.bytes) <= custom_end
        )

    def read_variable_length(self) -> bytes:
        """Reads and returns variable length encoded bytes."""
        return self.read(self._read_length_prefix())

    def _read_length_prefix(self) -> int:
        """
        Reads a variable length encoding prefix and returns the encoded length.

        The formula for decoding a length prefix is described in:
        `Length Prefixing <https://xrpl.org/serialization.html#length-prefixing>`_
        """
        byte1 = self.read_uint8()
        # If the field contains 0 to 192 bytes of data, the first byte defines
        # the length of the contents
        if byte1 <= MAX_SINGLE_BYTE_LENGTH:
            return byte1
        # If the field contains 193 to 12480 bytes of data, the first two bytes
        # indicate the length of the field with the following formula:
        #    193 + ((byte1 - 193) * 256) + byte2
        if byte1 <= MAX_SECOND_BYTE_VALUE:
            byte2 = self.read_uint8()
            return (
                (MAX_SINGLE_BYTE_LENGTH + 1)
                + ((byte1 - (MAX_SINGLE_BYTE_LENGTH + 1)) * MAX_BYTE_VALUE)
                + byte2
            )
        # If the field contains 12481 to 918744 bytes of data, the first three
        # bytes indicate the length of the field with the following formula:
        #    12481 + ((byte1 - 241) * 65536) + (byte2 * 256) + byte3
        if byte1 <= 254:
            byte2 = self.read_uint8()
            byte3 = self.read_uint8()
            return (
                MAX_DOUBLE_BYTE_LENGTH
                + ((byte1 - (MAX_SECOND_BYTE_VALUE + 1)) * MAX_DOUBLE_BYTE_VALUE)
                + (byte2 * MAX_BYTE_VALUE)
                + byte3
            )
        raise XRPLBinaryCodecException(
            "Length prefix must contain between 1 and 3 bytes."
        )

    def read_field_header(self) -> FieldHeader:
        """Reads field ID from BinaryParser and returns as a FieldHeader object."""
        type_code = self.read_uint8()
        field_code = type_code & 15
        type_code >>= 4

        if type_code == 0:
            type_code = self.read_uint8()
            if type_code == 0 or type_code < 16:
                raise XRPLBinaryCodecException(
                    "Cannot read Field ID, type_code out of range."
                )

        if field_code == 0:
            field_code = self.read_uint8()
            if field_code == 0 or field_code < 16:
                raise XRPLBinaryCodecException(
                    "Cannot read field ID, field_code out of range."
                )
        return FieldHeader(type_code, field_code)

    def read_field(self) -> FieldInstance:
        """
        Read the field ordinal at the head of the BinaryParser and return a
        FieldInstance object representing information about the field contained
        in the following bytes.
        """
        field_header = self.read_field_header()
        field_name = definitions.get_field_name_from_header(field_header)
        return definitions.get_field_instance(field_name)

    def read_type(self, field_type: SerializedType):
        """Read next bytes from BinaryParser as the given type."""
        return field_type.from_parser(self)

    def read_field_value(self, field: FieldInstance) -> SerializedType:
        """Read value of the type specified by field from the BinaryParser."""
        field_type = self.type_for_field(field)
        # TODO: error handling for unsupported type?
        size_hint = (
            self.read_variable_length_length()
            if field.is_variable_length_encoded
            else None
        )
        value = field_type.from_parser(self, size_hint)
        if value is None:
            raise XRPLBinaryCodecException(
                "from_parser for {}, {} returned None.".format(field.name, field.type)
            )
        return value

    def read_field_and_value(self) -> Tuple[FieldInstance, SerializedType]:
        """Get the next field and value from the BinaryParser."""
        field = self.read_field()
        return field, self.read_field_value(field)
