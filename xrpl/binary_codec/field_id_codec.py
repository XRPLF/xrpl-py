from .definitions import FieldHeader, DefinitionService

class FieldIDCodec:
    """
    A class for encoding and decoding Field IDs.
    `Field IDs <https://xrpl.org/serialization.html#field-ids>`_
    """
    def __init__(self):
        self.definition_service = DefinitionService()

    def encodeFieldID(self, field_header):
        """
        Returns the unique Field ID for a given field name.
        This field ID consists of the type code and field code, in 1 to 3 bytes
        depending on whether those values are "common" (<16) or "uncommon" (>=16)
        """
        type_code = field_header.type_code
        field_code = field_header.field_code

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

    def decodeFieldID(self, field_id):
        """
        Returns a FieldHeader object representing the type code and field code of a decoded Field ID.
        """
        # TODO: implement specific errors
        assert len(field_id) > 0
        byte_array = bytearray.fromhex(field_id)
        if len(byte_array) == 1:
            high_bits = byte_array[0][:4]
            low_bits = byte_array[0][4:]
            return FieldHeader(int(high_bits, 16), int(low_bits, 16))
        elif len(byte_array) == 2:
            return "Unimplemented"
        elif len(byte_array) == 3:
            return "Unimplemented"
        else:
            raise Exception("Too many bytes in the FieldID")


    def uint8_to_bytes(self, i):
        return i.to_bytes(1, byteorder="big", signed=False)