import unittest
import xrpl.binary_codec.field_id_codec as field_id_codec
from xrpl.binary_codec.definitions import FieldHeader
from .fixtures import data_driven_fixtures


class TestFieldIDCodec(unittest.TestCase):
    """
    `See FieldIDs <https://xrpl.org/serialization.html#field-ids>`_
    """

    def setUp(self):
        self.field_tests = data_driven_fixtures.get_field_tests()

    def test_encode(self):
        for test in self.field_tests:
            # .hex().upper() just formats the resulting bytes for comparison
            # with upper case hex string in fixture data
            self.assertEqual(
                test.expected_hex, field_id_codec.encode(test.name).hex().upper()
            )

    def test_decode(self):
        for test in self.field_tests:
            self.assertEqual(test.name, field_id_codec.decode(test.expected_hex))

    def test_encode_field_id_1_byte(self):
        # field header representing an Expiration field (type code = 2, field code = 10)
        field_header = FieldHeader(2, 10)
        # type code: decimal 2 = 0010  field code: decimal 10 = 1010
        expected_field_id = bytes([int("0b00101010", 2)])
        field_id = field_id_codec._encode_field_id(field_header)
        self.assertEqual(expected_field_id, field_id)

    def test_encode_field_id_2_bytes_large_type_code(self):
        # field header representing a Paths field (type code = 18, field code = 1)
        field_header = FieldHeader(18, 1)
        # high 4 are 0: 0000; next 4 are field code: decimal 1 = 0001;
        # second byte is type code: decimal 18 = 00010010
        expected_field_id = bytes([int("0b00000001", 2), int("0b00010010", 2)])
        field_id = field_id_codec._encode_field_id(field_header)
        self.assertEqual(expected_field_id, field_id)

    def test_encode_field_id_2_bytes_large_field_code(self):
        # field header representing a QualityIn field (type code = 2, field code = 20)
        field_header = FieldHeader(2, 20)
        # high 4 are type code: 0010; next 4 are zero: 0000;
        # second byte is field code: decimal 20 = 00010100
        expected_field_id = bytes([int("0b00100000", 2), int("0b00010100", 2)])
        field_id = field_id_codec._encode_field_id(field_header)
        self.assertEqual(expected_field_id, field_id)

    def test_encode_field_id_3_bytes(self):
        # field header representing a TickSize field (type code = 16, field code = 16)
        field_header = FieldHeader(16, 16)
        # first byte is zero: 00000000; next byte is type code: 16 = 00010000;
        # last byte is field code: 16 = 00010000
        expected_field_id = bytes(
            [int("0b00000000", 2), int("0b00010000", 2), int("0b00010000", 2)]
        )
        field_id = field_id_codec._encode_field_id(field_header)
        self.assertEqual(expected_field_id, field_id)

    def test_decode_field_id_1_byte(self):
        # hex representing an Expiration field (type code = 2, field code = 10)
        field_id = bytes([int("0b00101010", 2)]).hex()
        expected_field_header = FieldHeader(2, 10)
        field_header = field_id_codec._decode_field_id(field_id)
        self.assertEqual(expected_field_header, field_header)

    def test_decode_field_id_2_bytes_large_type_code(self):
        # hex representing a Paths field (type code = 18, field code = 1)
        field_id = bytes([int("0b00000001", 2), int("0b00010010", 2)]).hex()
        expected_field_header = FieldHeader(18, 1)
        field_header = field_id_codec._decode_field_id(field_id)
        self.assertEqual(expected_field_header, field_header)

    def test_decode_field_id_2_bytes_large_field_code(self):
        # hex representing a QualityIn field (type code = 2, field code = 20)
        field_id = bytes([int("0b00100000", 2), int("0b00010100", 2)]).hex()
        expected_field_header = FieldHeader(2, 20)
        field_header = field_id_codec._decode_field_id(field_id)
        self.assertEqual(expected_field_header, field_header)

    def test_decode_field_id_3_bytes(self):
        # hex representing a TickSize field (type code = 16, field code = 16)
        field_id = bytes(
            [int("0b00000000", 2), int("0b00010000", 2), int("0b00010000", 2)]
        ).hex()
        expected_field_header = FieldHeader(16, 16)
        field_header = field_id_codec._decode_field_id(field_id)
        self.assertEqual(expected_field_header, field_header)
