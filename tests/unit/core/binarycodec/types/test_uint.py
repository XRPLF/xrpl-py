from unittest import TestCase

from xrpl.core.binarycodec import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.uint8 import UInt8
from xrpl.core.binarycodec.types.uint16 import UInt16
from xrpl.core.binarycodec.types.uint32 import UInt32
from xrpl.core.binarycodec.types.uint64 import UInt64


class TestUInt(TestCase):
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

        self.assertEqual(value1, 124)
        self.assertLess(value1, 125)
        self.assertGreater(value1, 123)

    def test_compare_different(self):
        const = 124
        uint8 = UInt8.from_value(const)
        uint16 = UInt16.from_value(const)
        uint32 = UInt32.from_value(const)
        uint64 = UInt64.from_value(const)

        self.assertEqual(uint8, uint16)
        self.assertEqual(uint16, uint32)
        self.assertEqual(uint32, uint64)
        self.assertEqual(uint64, const)

    def test_raises_invalid_value_type(self):
        invalid_value = [1, 2, 3]
        self.assertRaises(XRPLBinaryCodecException, UInt8.from_value, invalid_value)
        self.assertRaises(XRPLBinaryCodecException, UInt16.from_value, invalid_value)
        self.assertRaises(XRPLBinaryCodecException, UInt32.from_value, invalid_value)
        self.assertRaises(XRPLBinaryCodecException, UInt64.from_value, invalid_value)
