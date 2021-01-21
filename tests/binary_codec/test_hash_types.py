import unittest
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.binary_wrappers import BinaryParser
from xrpl.binary_codec.types import Hash160


class TestHash160(unittest.TestCase):
    def setUp(self):
        # 20 bytes, 40 nibbles
        self.hex_160_bits = "1000000000200000000030000000004000000000"
        self.parser = BinaryParser(self.hex_160_bits)

    def test_constructors(self):
        pass
        from_constructor = Hash160(bytes.fromhex(self.hex_160_bits))
        from_value = Hash160.from_value(self.hex_160_bits)
        from_parser = Hash160.from_parser(self.parser)

        self.assertEqual(from_constructor.to_hex(), self.hex_160_bits)
        self.assertEqual(from_value.to_hex(), self.hex_160_bits)
        self.assertEqual(from_parser.to_hex(), self.hex_160_bits)

    def test_constructor_raises_invalid_length(self):
        # 21 bytes, 42 nibbles
        too_many_bytes_hex = "100000000020000000003000000000400000000012"
        self.assertRaises(
            XRPLBinaryCodecException, Hash160.from_value, too_many_bytes_hex
        )

    # test construction from incorrect length throws

    # test that it has a width field == 20?

    # test (/write?) comparison operators

    # test inherited methods from SerializedType:
    # to_byte_sink(self, bytesink):
    # to_bytes(self):
    # to_json(self):
    # to_string(self):
    # to_hex(self):
