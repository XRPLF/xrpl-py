from xrpl.binary_codec.exceptions import XRPLBinaryCodecException


class BinaryParser:
    """ Deserializes from hex-encoded XRPL binary format to JSON fields and values."""

    def __init__(self, hex_bytes):
        self.bytes = bytes.fromhex(hex_bytes)

    def peek(self):
        """ Peek the first byte of the BinaryParser. """
        assert len(self.bytes) > 0
        return self.bytes[0]

    def skip(self, n):
        """ Consume the first n bytes of the BinaryParser. """
        assert n <= len(self.bytes)
        self.bytes = self.bytes[n:]

    def read(self, n):
        """ Consume and return the first n bytes of the BinaryParser. """
        assert n <= len(self.bytes)
        first_n_bytes = self.bytes[n:]
        self.skip(n)
        return first_n_bytes

    def read_uint_n(self, n):
        """
        Reads an integer of given size in bytes.

        Parameters:
            n: The number of bytes to read.
        Returns:
            The integer represented by those bytes.
        """
        assert 0 < n <= 4
        return int.from_bytes(b"".join(self.read(n)), byteorder="big", signed=False)

    def read_uint_8(self):
        return self.read_uint_n(1)

    def read_uint_16(self):
        return self.read_uint_n(2)

    def read_uint_32(self):
        return self.read_uint_n(4)

    # TODO: should this be a __len__ override?
    def size(self):
        return len(self.bytes)

    def end(self, custom_end=None):
        return len(self.bytes) == 0 or (
            custom_end is not None and len(self.bytes) <= custom_end
        )

    def read_variable_length(self):
        """ Reads and returns variable length encoded bytes. """
        return self.read(self.read_variable_length_length())

    def read_variable_length_length(self):
        """
        Reads a variable length encoding prefix and returns the encoded length.

        The formula for decoding a length prefix is described in:
        `Length Prefixing <https://xrpl.org/serialization.html#length-prefixing>`_
        """
        byte1 = self.read_uint_8()
        # If the field contains 0 to 192 bytes of data, the first byte defines
        # the length of the contents
        if byte1 <= 192:
            return byte1
        # If the field contains 193 to 12480 bytes of data, the first two bytes
        # indicate the length of the field with the following formula:
        #    193 + ((byte1 - 193) * 256) + byte2
        if byte1 <= 240:
            byte2 = self.read_uint_8()
            return 193 + ((byte1 - 193) * 256) + byte2
        # If the field contains 12481 to 918744 bytes of data, the first three
        # bytes indicate the length of the field with the following formula:
        #    12481 + ((byte1 - 241) * 65536) + (byte2 * 256) + byte3
        if byte1 <= 254:
            byte2 = self.read_uint_8()
            byte3 = self.read_uint_8()
            return 12481 + ((byte1 - 241) * 65536) + (byte2 * 256) + byte3
        raise XRPLBinaryCodecException(
            "Length prefix must contain between 1 and 3 bytes."
        )

    """
  /**
   * Reads the field ordinal from the BinaryParser
   *
   * @return Field ordinal
   */
  readFieldOrdinal(): number {
    let type = this.readUInt8();
    let nth = type & 15;
    type >>= 4;

    if (type === 0) {
      type = this.readUInt8();
      if (type === 0 || type < 16) {
        throw new Error("Cannot read FieldOrdinal, type_code out of range");
      }
    }

    if (nth === 0) {
      nth = this.readUInt8();
      if (nth === 0 || nth < 16) {
        throw new Error("Cannot read FieldOrdinal, field_code out of range");
      }
    }

    return (type << 16) | nth;
  }

  /**
   * Read the field from the BinaryParser
   *
   * @return The field represented by the bytes at the head of the BinaryParser
   */
  readField(): FieldInstance {
    return Field.fromString(this.readFieldOrdinal().toString());
  }

  /**
   * Read a given type from the BinaryParser
   *
   * @param type The type that you want to read from the BinaryParser
   * @return The instance of that type read from the BinaryParser
   */
  readType(type: typeof SerializedType): SerializedType {
    return type.fromParser(this);
  }

  /**
   * Get the type associated with a given field
   *
   * @param field The field that you wan to get the type of
   * @return The type associated with the given field
   */
  typeForField(field: FieldInstance): typeof SerializedType {
    return field.associatedType;
  }

  /**
   * Read value of the type specified by field from the BinaryParser
   *
   * @param field The field that you want to get the associated value for
   * @return The value associated with the given field
   */
  readFieldValue(field: FieldInstance): SerializedType {
    const type = this.typeForField(field);
    if (!type) {
      throw new Error(`unsupported: (${field.name}, ${field.type.name})`);
    }
    const sizeHint = field.isVariableLengthEncoded
      ? this.readVariableLengthLength()
      : undefined;
    const value = type.fromParser(this, sizeHint);
    if (value === undefined) {
      throw new Error(
        `fromParser for (${field.name}, ${field.type.name}) -> undefined `
      );
    }
    return value;
  }

  /**
   * Get the next field and value from the BinaryParser
   *
   * @return The field and value
   */
  readFieldAndValue(): [FieldInstance, SerializedType] {
    const field = this.readField();
    return [field, this.readFieldValue(field)];
  }
}

"""
