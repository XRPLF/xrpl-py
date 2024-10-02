from unittest import TestCase

from xrpl.utils import hex_to_int, int_to_hex

_ORIGINAL = 9223372036854775807
_HEX = "7fffffffffffffff"


class TestIntConversions(TestCase):
    def test_int_to_hex(self):
        self.assertTrue(int_to_hex(_ORIGINAL) == _HEX)

    def test_hex_to_int(self):
        self.assertTrue(hex_to_int(_HEX) == _ORIGINAL)
