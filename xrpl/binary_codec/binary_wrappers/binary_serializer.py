# Constants used in length prefix encoding:
# max length that can be represented in a single byte per XRPL serialization encoding
MAX_SINGLE_BYTE_LENGTH = 192
# max length that can be represented in 2 bytes per XRPL serialization encoding
MAX_DOUBLE_BYTE_LENGTH = 12481
# max value that can be used in the second byte of a length field
MAX_SECOND_BYTE_VALUE = 240
# maximum length that can be encoded in a length prefix per XRPL serialization encoding
MAX_LENGTH_VALUE = 918744


class BinarySerializer:
    """
    Serializes JSON to XRPL binary format.
    """

    def __init__(self):
        self.bytesink = bytes()

    def put(self, hex_bytes):
        self.bytesink.append(bytes.fromhex(hex_bytes))

    def write(self, byte_array):
        self.bytesink.append(byte_array)

    def encode_variable_length_prefix(self, length):
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

    # TODO: this method depends on the SerializedType class.
    def write_length_encoded(self, value):
        """
        Write a variable length encoded value to the BinarySerializer.
        """
        pass

    # TODO: this method depends on the SerializedType and FieldInstance classes.
    def write_field_and_value(self, field, value):
        """
        Write field and value to the buffer.
        """
        return None
