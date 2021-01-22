import unittest

from xrpl.binary_codec.types import UInt8


class TestUInt(unittest.TestCase):
    def test_from_value(self):
        value1 = UInt8.from_value(124)
        value2 = UInt8.from_value(123)
        value3 = UInt8.from_value(124)

        self.assertGreater(value1, value2)
        self.assertLess(value2, value1)
        self.assertNotEqual(value1, value2)
        self.assertEqual(value1, value3)

    def test_compare(self):
        value1 = UInt8.from_value(124)
        value1_value = int.from_bytes(value1.buffer, byteorder="big")

        self.assertEqual(value1_value, 124)
        self.assertLess(value1_value, 125)
        self.assertGreater(value1_value, 123)
