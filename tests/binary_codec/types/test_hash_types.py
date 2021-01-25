import unittest

from xrpl.binary_codec.binary_wrappers import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.hash128 import Hash128
from xrpl.binary_codec.types.hash160 import Hash160
from xrpl.binary_codec.types.hash256 import Hash256


class TestHash128(unittest.TestCase):
    def setUp(self):
        # 16 bytes, 32 nibbles
        self.hex_128_bits = "10000000002000000000300000000012"
        self.parser = BinaryParser(self.hex_128_bits)
        self.expected_width = 16

    def test_constructors(self):
        from_constructor = Hash128(bytes.fromhex(self.hex_128_bits))
        from_value = Hash128.from_value(self.hex_128_bits)
        from_parser = Hash128.from_parser(self.parser)

        self.assertEqual(from_constructor.to_hex(), self.hex_128_bits)
        self.assertEqual(from_value.to_hex(), self.hex_128_bits)
        self.assertEqual(from_parser.to_hex(), self.hex_128_bits)

        # Assert objects have correct width
        self.assertEqual(from_constructor._width, self.expected_width)
        self.assertEqual(from_value._width, self.expected_width)
        self.assertEqual(from_parser._width, self.expected_width)

    def test_constructor_raises_invalid_length(self):
        # 17 bytes, 34 nibbles
        too_many_bytes_hex = "1000000000200000000030000000001234"
        self.assertRaises(
            XRPLBinaryCodecException, Hash128.from_value, too_many_bytes_hex
        )


class TestHash160(unittest.TestCase):
    def setUp(self):
        # 20 bytes, 40 nibbles
        self.hex_160_bits = "1000000000200000000030000000004000000000"
        self.parser = BinaryParser(self.hex_160_bits)
        self.expected_width = 20

    def test_constructors(self):
        from_constructor = Hash160(bytes.fromhex(self.hex_160_bits))
        from_value = Hash160.from_value(self.hex_160_bits)
        from_parser = Hash160.from_parser(self.parser)

        self.assertEqual(from_constructor.to_hex(), self.hex_160_bits)
        self.assertEqual(from_value.to_hex(), self.hex_160_bits)
        self.assertEqual(from_parser.to_hex(), self.hex_160_bits)

        # Assert objects have correct width
        self.assertEqual(from_constructor._width, self.expected_width)
        self.assertEqual(from_value._width, self.expected_width)
        self.assertEqual(from_parser._width, self.expected_width)

    def test_constructor_raises_invalid_length(self):
        # 21 bytes, 42 nibbles
        too_many_bytes_hex = "100000000020000000003000000000400000000012"
        self.assertRaises(
            XRPLBinaryCodecException, Hash160.from_value, too_many_bytes_hex
        )


class TestHash256(unittest.TestCase):
    def setUp(self):
        # 32 bytes, 64 nibbles
        self.hex_256_bits = (
            "1000000000200000000030000000004000000000500000000060000000001234"
        )
        self.parser = BinaryParser(self.hex_256_bits)
        self.expected_width = 32

    def test_constructors(self):
        from_constructor = Hash256(bytes.fromhex(self.hex_256_bits))
        from_value = Hash256.from_value(self.hex_256_bits)
        from_parser = Hash256.from_parser(self.parser)

        self.assertEqual(from_constructor.to_hex(), self.hex_256_bits)
        self.assertEqual(from_value.to_hex(), self.hex_256_bits)
        self.assertEqual(from_parser.to_hex(), self.hex_256_bits)

        # Assert objects have correct width
        self.assertEqual(from_constructor._width, self.expected_width)
        self.assertEqual(from_value._width, self.expected_width)
        self.assertEqual(from_parser._width, self.expected_width)

    def test_constructor_raises_invalid_length(self):
        # 33 bytes, 66 nibbles
        too_many_bytes_hex = (
            "100000000020000000003000000000400000000050000000006000000000123456"
        )
        self.assertRaises(
            XRPLBinaryCodecException, Hash256.from_value, too_many_bytes_hex
        )
