import unittest

from xrpl import binary_codec


class TestBinaryParser(unittest.TestCase):
    def setUp(self):
        test_hex = "00112233445566"
        self.test_bytes = bytes.fromhex(test_hex)
        self.binary_parser = binary_codec.BinaryParser(test_hex)

    def test_peek_skip_read_methods(self):
        first_byte = self.binary_parser.peek()
        self.assertEqual(first_byte, self.test_bytes[0])

        self.binary_parser.skip(3)
        self.assertEqual(self.test_bytes[3:], self.binary_parser.bytes)

        next_n_bytes = self.binary_parser.read(2)
        self.assertEqual(self.test_bytes[3:5], next_n_bytes)

    def test_int_read_methods(self):
        pass

    def test_read_variable_length_length(self):
        pass
