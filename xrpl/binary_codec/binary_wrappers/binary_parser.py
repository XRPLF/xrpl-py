"""TODO: D100 Missing docstring in public module."""
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.definitions import definitions
from xrpl.binary_codec.definitions.field_header import FieldHeader
from xrpl.binary_codec.definitions.field_instance import FieldInstance
from xrpl.binary_codec.types.serialized_type import SerializedType

# Constants used in length prefix decoding:
# max length that can be represented in a single byte per XRPL serialization encoding
MAX_SINGLE_BYTE_LENGTH = 192
# max length that can be represented in 2 bytes per XRPL serialization restrictions
MAX_DOUBLE_BYTE_LENGTH = 12481
# max value that can be used in the second byte of a length field
MAX_SECOND_BYTE_VALUE = 240
# max value that can be represented using one 8-bit byte (2^8)
MAX_BYTE_VALUE = 256
# max value that can be represented in using two 8-bit bytes (2^16)
MAX_DOUBLE_BYTE_VALUE = 65536


class BinaryParser:
    """Deserializes from hex-encoded XRPL binary format to JSON fields and values."""

    def __init__(self, hex_bytes):
        """TODO: D107 Missing docstring in __init__."""
        self.bytes = bytes.fromhex(hex_bytes)

    def peek(self):
        """Peek the first byte of the BinaryParser."""
        assert len(self.bytes) > 0
        return self.bytes[0]

    def skip(self, n):
        """Consume the first n bytes of the BinaryParser."""
        assert n <= len(self.bytes)
        self.bytes = self.bytes[n:]

    def read(self, n):
        """Consume and return the first n bytes of the BinaryParser."""
        assert n <= len(self.bytes)
        first_n_bytes = self.bytes[:n]
        self.skip(n)
        return first_n_bytes

    def read_uint8(self):
        """TODO: D102 Missing docstring in public method."""
        return int.from_bytes(self.read(1), byteorder="big")

    def read_uint16(self):
        """TODO: D102 Missing docstring in public method."""
        return int.from_bytes(self.read(2), byteorder="big")

    def read_uint32(self):
        """TODO: D102 Missing docstring in public method."""
        return int.from_bytes(self.read(4), byteorder="big")

    # TODO: should this be a __len__ override?
    def size(self):
        """TODO: D102 Missing docstring in public method."""
        return len(self.bytes)

    def end(self, custom_end=None):
        """TODO: D102 Missing docstring in public method."""
        return len(self.bytes) == 0 or (
            custom_end is not None and len(self.bytes) <= custom_end
        )

    def read_variable_length(self):
        """Reads and returns variable length encoded bytes."""
        return self.read(self.read_variable_length_length())

    def read_variable_length_length(self):
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

    def read_field_header(self):
        """Reads field ordinal from BinaryParser and returns as a FieldHeader object."""
        type_code = self.read_uint8()
        field_code = type & 15
        type_code >>= 4

        if type_code == 0:
            type_code = self.read_uint8()
            if type_code == 0 or type_code < 16:
                raise XRPLBinaryCodecException(
                    "Cannot read FieldOrdinal, type_code out of range."
                )

        if field_code == 0:
            field_code = self.read_uint8()
            if field_code == 0 or field_code < 16:
                raise XRPLBinaryCodecException(
                    "Cannot read FieldOrdinal, field_code out of range."
                )
        return FieldHeader(type_code, field_code)

    def read_field(self):
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

    def type_for_field(self, field_instance: FieldInstance):
        """Get the type associated with a given field."""
        return field_instance.type

    def read_field_value(self, field: FieldInstance):
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

    def read_field_and_value(self):
        """Get the next field and value from the BinaryParser."""
        field = self.read_field()
        return field, self.read_field_value(field)
