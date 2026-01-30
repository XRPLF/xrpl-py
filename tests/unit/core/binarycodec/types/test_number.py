import unittest

from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.number import (
    _MAX_EXPONENT,
    _MAX_MANTISSA,
    _MIN_EXPONENT,
    _MIN_MANTISSA,
    Number,
)


class TestNumber(unittest.TestCase):
    def test_serialization_and_deserialization(self):
        serialized_number = Number.from_value("124")
        self.assertEqual(serialized_number.to_json(), "124")

        serialized_number = Number.from_value("1000")
        self.assertEqual(serialized_number.to_json(), "1000")

        serialized_number = Number.from_value("0")
        self.assertEqual(serialized_number.to_json(), "0")

        serialized_number = Number.from_value("-1")
        self.assertEqual(serialized_number.to_json(), "-1")

        serialized_number = Number.from_value("1")
        self.assertEqual(serialized_number.to_json(), "1")

        serialized_number = Number.from_value("123.456")
        self.assertEqual(serialized_number.to_json(), "123.456")

        serialized_number = Number.from_value("-987.654")
        self.assertEqual(serialized_number.to_json(), "-987.654")

        serialized_number = Number.from_value("1.456e-45")
        self.assertEqual(serialized_number.to_json(), "1456e-48")

        serialized_number = Number.from_value("0.456e34")
        self.assertEqual(serialized_number.to_json(), "456e31")

        serialized_number = Number.from_value("-4e34")
        self.assertEqual(serialized_number.to_json(), "-4e34")

        serialized_number = Number.from_value("-1.234e34")
        self.assertEqual(serialized_number.to_json(), "-1234e31")

    def test_serialized_repr(self):
        lowest_mantissa = "-9223372036854776"
        # Note: The value undergoes normalization before being stored in serialized
        # form. This value is stored as mantissa=-922337203685477600, exponent=-2
        serialized_number = Number.from_value(lowest_mantissa)
        self.assertEqual(
            serialized_number.display_serialized_hex(), "F333333333333320" + "FFFFFFFE"
        )

        highest_mantissa = "9223372036854776"
        # This number is stored as mantissa=922337203685477600, exponent=-2
        serialized_number = Number.from_value(highest_mantissa)
        self.assertEqual(
            serialized_number.display_serialized_hex(), "0CCCCCCCCCCCCCE0" + "FFFFFFFE"
        )

    def test_equivalent_normalized_forms(self):
        self.assertEqual(
            Number.from_mantissa_exponent(
                _mantissa=_MIN_MANTISSA * 10, _exponent=32767
            ).to_json(),
            Number.from_mantissa_exponent(
                _mantissa=_MIN_MANTISSA, _exponent=32768
            ).to_json(),
        )

    def test_overflow(self):
        with self.assertRaises(XRPLBinaryCodecException):
            Number.from_mantissa_exponent(_MAX_MANTISSA + 1, _MAX_EXPONENT)

    def test_underflow(self):
        self.assertEqual(
            Number.from_mantissa_exponent(
                _mantissa=_MIN_MANTISSA, _exponent=-32769
            ).to_json(),
            Number.from_value("0").to_json(),
        )
