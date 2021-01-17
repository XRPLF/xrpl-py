import unittest

from xrpl.binary_codec.binary_wrappers import BinaryParser, BinarySerializer

"""
Note that core field-reading logic will be tested by the implementation of
specific field type classes. These tests just sanity-check key helper methods.
"""


class TestBinaryParser(unittest.TestCase):
    def test_peek_skip_read_methods(self):
        test_hex = "00112233445566"
        test_bytes = bytes.fromhex(test_hex)
        binary_parser = BinaryParser(test_hex)

        first_byte = binary_parser.peek()
        self.assertEqual(first_byte, test_bytes[0])

        binary_parser.skip(3)
        self.assertEqual(test_bytes[3:], binary_parser.bytes)

        next_n_bytes = binary_parser.read(2)
        self.assertEqual(test_bytes[3:5], next_n_bytes)

    def test_int_read_methods(self):
        test_hex = "01000200000003"
        binary_parser = BinaryParser(test_hex)

        int8 = binary_parser.read_uint8()
        int16 = binary_parser.read_uint16()
        int32 = binary_parser.read_uint32()

        self.assertEqual(int8, 1)
        self.assertEqual(int16, 2)
        self.assertEqual(int32, 3)

    def test_read_variable_length_length(self):
        binary_serializer = BinarySerializer()
        for case in [100, 1000, 20_000]:
            # hex string representation of encoded length prefix
            encoded_length = binary_serializer.encode_variable_length_prefix(case).hex()
            binary_parser = BinaryParser(encoded_length)
            decoded_length = binary_parser.read_variable_length_length()
            self.assertEqual(case, decoded_length)
