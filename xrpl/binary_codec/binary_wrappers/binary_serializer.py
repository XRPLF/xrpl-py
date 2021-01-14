class BinarySerializer:
    """
    Serializes JSON to XRPL binary format.
    """
    def __init__(self):
        self.sink = bytes()

    def put(self, hex_bytes):
        self.sink.append(bytes.fromhex(hex_bytes))

    def write(self, byte_array):
        self.sink.append(byte_array)

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
        if length <= 192:
            return length.to_bytes(1, byteorder="big", signed=False)
        elif length <= 12480:
            length -= 193
            byte1 = ((length >> 8) + 193).to_bytes(1, byteorder="big", signed=False)
            byte2 = (length & 0xff).to_bytes(1, byteorder="big", signed=False)
            return b''.join((byte1, byte2))
        elif length <= 918744:
            length -= 12481
            byte1 = (241 + (length >> 16)).to_bytes(1, byteorder="big", signed=False)
            byte2 = ((length >> 8) & 0xff).to_bytes(1, byteorder="big", signed=False)
            byte3 = (length & 0xff).to_bytes(1, byteorder="big", signed=False)
            return b''.join((byte1, byte2, byte3))

        raise ValueError("VariableLength field must be <= 918744 bytes long")

    # TODO: this method depends on the SerializedType class (of which value is a member).
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



