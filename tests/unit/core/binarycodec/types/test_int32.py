from unittest import TestCase

from xrpl.core.binarycodec import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.int32 import Int32


class TestUInt(TestCase):
    def test_compare_INT32(self):
        value1 = Int32.from_value(124)
        value2 = Int32.from_value(123)
        value3 = Int32.from_value(124)

        self.assertGreater(value1, value2)
        self.assertLess(value2, value1)
        self.assertNotEqual(value1, value2)
        self.assertEqual(value1, value3)

    def test_from_value(self):
        self.assertEqual(Int32.from_value(0).to_json(), 0)
        self.assertEqual(Int32.from_value(110).to_json(), 110)
        self.assertEqual(Int32.from_value(-123).to_json(), -123)

    def test_limits(self):
        self.assertEqual(Int32.from_value(-2147483648).to_json(), -2147483648)
        self.assertEqual(Int32.from_value(2147483647).to_json(), 2147483647)

    def test_compare(self):
        value1 = Int32.from_value(124)

        self.assertEqual(value1, 124)
        self.assertLess(value1, 1000)
        self.assertGreater(value1, -1000)

    def test_raises_invalid_value_type(self):
        invalid_value = [1, 2, 3]
        self.assertRaises(XRPLBinaryCodecException, Int32.from_value, invalid_value)
