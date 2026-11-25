from unittest import TestCase

from xrpl.core.binarycodec import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.currency import Currency
from xrpl.core.binarycodec.types.st_array import STArray
from xrpl.core.binarycodec.types.uint16 import UInt16
from xrpl.core.binarycodec.types.uint32 import UInt32
from xrpl.core.binarycodec.types.vector256 import Vector256


class TestFromValueErrorMessages(TestCase):
    def test_currency_unsupported_representation_message_interpolates(self):
        with self.assertRaises(XRPLBinaryCodecException) as ctx:
            Currency.from_value("ZZZ-not-hex-not-iso")
        msg = str(ctx.exception)
        self.assertNotIn("{value", msg)
        self.assertIn("ZZZ-not-hex-not-iso", msg)

    def test_st_array_invalid_type_message_interpolates(self):
        with self.assertRaises(XRPLBinaryCodecException) as ctx:
            STArray.from_value(5)
        msg = str(ctx.exception)
        self.assertNotIn("{value", msg)
        self.assertIn("received int.", msg)

    def test_uint16_invalid_type_message_interpolates(self):
        with self.assertRaises(XRPLBinaryCodecException) as ctx:
            UInt16.from_value("not_an_int")
        msg = str(ctx.exception)
        self.assertNotIn("{value", msg)
        self.assertIn("received str.", msg)

    def test_uint32_invalid_type_message_interpolates(self):
        with self.assertRaises(XRPLBinaryCodecException) as ctx:
            UInt32.from_value([1, 2])
        msg = str(ctx.exception)
        self.assertNotIn("{value", msg)
        self.assertIn("received list.", msg)

    def test_vector256_invalid_type_message_interpolates(self):
        with self.assertRaises(XRPLBinaryCodecException) as ctx:
            Vector256.from_value("not_a_list")
        msg = str(ctx.exception)
        self.assertNotIn("{value", msg)
        self.assertIn("received str.", msg)
