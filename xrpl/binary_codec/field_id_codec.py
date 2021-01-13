from .definitions import FieldHeader, DefinitionService

class FieldIDCodec:
    """
    A class for encoding and decoding field IDs.
    `Field IDs <https://xrpl.org/serialization.html#field-ids>`_
    """
    def __init__(self):
        self.definition_service = DefinitionService()

    def encode(self, field_name):
        """
        Returns the unique field ID for a given field name.
        This field ID consists of the type code and field code, in 1 to 3 bytes
        depending on whether those values are "common" (<16) or "uncommon" (>=16)
        """
        field_header = self.definition_service.get_field_header_from_name(field_name)
        return self._encode_field_id(field_header)

    def decode(self, field_id):
        """
        Returns the field name represented by the given field ID.
        """
        field_header = self._decode_field_id(field_id)
        return self.definition_service.get_field_name_from_header(field_header)

    def _encode_field_id(self, field_header):
        """
        Returns the unique field ID for a given field header.
        This field ID consists of the type code and field code, in 1 to 3 bytes
        depending on whether those values are "common" (<16) or "uncommon" (>=16)
        """
        type_code = field_header.type_code
        field_code = field_header.field_code

        # TODO: implement specific errors
        # Codes must be nonzero and fit in 1 byte
        assert 0 < field_code <= 255
        assert 0 < type_code <= 255

        if type_code < 16 and field_code < 16:
            # high 4 bits is the type_code
            # low 4 bits is the field code
            combined_code = (type_code << 4) | field_code
            return self.uint8_to_bytes(combined_code)
        elif type_code >= 16 and field_code < 16:
            # first 4 bits are zeroes
            # next 4 bits is field code
            # next byte is type code
            byte1 = self.uint8_to_bytes(field_code)
            byte2 = self.uint8_to_bytes(type_code)
            return b''.join((byte1, byte2))
        elif type_code < 16 and field_code >= 16:
            # first 4 bits is type code
            # next 4 bits are zeroes
            # next byte is field code
            byte1 = self.uint8_to_bytes(type_code << 4)
            byte2 = self.uint8_to_bytes(field_code)
            return b''.join((byte1, byte2))
        else:  # both are >= 16
            # first byte is all zeroes
            # second byte is type code
            # third byte is field code
            byte2 = self.uint8_to_bytes(type_code)
            byte3 = self.uint8_to_bytes(field_code)
            return b''.join((bytes(1), byte2, byte3))

    def _decode_field_id(self, field_id):
        """
        Returns a FieldHeader object representing the type code and field code of a decoded field ID.
        """
        # TODO: implement specific errors
        assert len(field_id) > 0
        byte_array = bytearray.fromhex(field_id)
        if len(byte_array) == 1:
            high_bits = byte_array[0] >> 4
            low_bits = byte_array[0] & 0x0F
            return FieldHeader(high_bits, low_bits)
        elif len(byte_array) == 2:
            first_byte = byte_array[0]
            second_byte = byte_array[1]
            first_byte_high_bits = first_byte >> 4
            first_byte_low_bits = first_byte & 0x0F
            if first_byte_high_bits == 0:  # next 4 bits are field code, second byte is type code
                return FieldHeader(second_byte, first_byte_low_bits)
            else:  # next 4 bits are type code, second byte is field code
                return FieldHeader(first_byte_high_bits, second_byte)
        elif len(byte_array) == 3:
            return FieldHeader(byte_array[1], byte_array[2])
        else:
            raise Exception("Too many bytes in the field ID")

    def uint8_to_bytes(self, i):
        return i.to_bytes(1, byteorder="big", signed=False)