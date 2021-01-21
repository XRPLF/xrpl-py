import unittest
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.binary_wrappers import BinaryParser
from xrpl.binary_codec.types import Hash160


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
        self.assertEqual(from_constructor.width, self.expected_width)
        self.assertEqual(from_value.width, self.expected_width)
        self.assertEqual(from_parser.width, self.expected_width)

    def test_constructor_raises_invalid_length(self):
        # 21 bytes, 42 nibbles
        too_many_bytes_hex = "100000000020000000003000000000400000000012"
        self.assertRaises(
            XRPLBinaryCodecException, Hash160.from_value, too_many_bytes_hex
        )
