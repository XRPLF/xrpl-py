import unittest

from xrpl import binary_codec


class TestFieldIDCodec(unittest.TestCase):
    """
    `See FieldIDs <https://xrpl.org/serialization.html#field-ids>`_
    """
    def setUp(self):
        self.field_id_codec = binary_codec.FieldIDCodec()

    def test_encode_field_id_1_byte(self):
        # field header representing an Expiration field (type code = 2, field code = 10)
        field_header = binary_codec.FieldHeader(2, 10)
        # type code: decimal 2 = 0010  field code: decimal 10 = 1010
        expected_field_id = bytes([int('0b00101010', 2)])
        field_id = self.field_id_codec.encodeFieldID(field_header)
        self.assertEqual(expected_field_id, field_id)

    def test_encode_field_id_2_bytes_large_type_code(self):
        # field header representing a Paths field (type code = 18, field code = 1)
        field_header = binary_codec.FieldHeader(18, 1)
        # high 4 are 0: 0000; next 4 are field code: decimal 1 = 0001; second byte is type code: decimal 18 = 00010010
        expected_field_id = bytes([int('0b00000001', 2), int('0b00010010', 2)])
        field_id = self.field_id_codec.encodeFieldID(field_header)
        self.assertEqual(expected_field_id, field_id)

    def test_encode_field_id_2_bytes_large_field_code(self):
        # field header representing a QualityIn field (type code = 2, field code = 20)
        field_header = binary_codec.FieldHeader(2, 20)
        # high 4 are type code: 0010; next 4 are zero: 0000; second byte is field code: decimal 20 = 00010100
        expected_field_id = bytes([int('0b00100000', 2), int('0b00010100', 2)])
        field_id = self.field_id_codec.encodeFieldID(field_header)
        self.assertEqual(expected_field_id, field_id)

    def test_encode_field_id_4_bytes(self):
        # field header representing a TickSize field (type code = 16, field code = 16)
        field_header = binary_codec.FieldHeader(16, 16)
        # first byte is zero: 00000000; next byte is type code: 16 = 00010000; last byte is field code: 16 = 00010000
        expected_field_id = bytes([int('0b00000000', 2), int('0b00010000', 2), int('0b00010000', 2)])
        field_id = self.field_id_codec.encodeFieldID(field_header)
        self.assertEqual(expected_field_id, field_id)