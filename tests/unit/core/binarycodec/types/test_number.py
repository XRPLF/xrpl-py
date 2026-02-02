import unittest

from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.number import (
    _MAX_EXPONENT,
    _MAX_MANTISSA,
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

        # test the round-trip of a large value
        _number = "99999999999999984e79"
        self.assertEqual(Number.from_value(_number).to_json(), _number)

        _number = "9999999999999999e80"
        self.assertEqual(Number.from_value(_number).to_json(), _number)

        # large value with trailing zeros
        self.assertEqual(Number.from_value("9900000000000000000000").to_json(), "99e20")
        # small value with leading zeros
        self.assertEqual(
            Number.from_value("0.0000000000000000000099").to_json(), "99e-22"
        )

        # test the instances where scientific notation is used
        self.assertEqual(Number.from_value("-100000000000").to_json(), "-1e11")
        self.assertEqual(Number.from_value("-10000000000").to_json(), "-10000000000")
        self.assertEqual(Number.from_value("0.00000000001").to_json(), "1e-11")
        self.assertEqual(Number.from_value("0.0001").to_json(), "0.0001")

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

        with self.assertRaises(XRPLBinaryCodecException):
            print(Number.from_value("1e40000").to_json())

    def test_underflow(self):
        self.assertEqual(
            Number.from_mantissa_exponent(
                _mantissa=_MIN_MANTISSA, _exponent=-32769
            ).to_json(),
            Number.from_value("0").to_json(),
        )

        self.assertEqual(
            Number.from_value("1e-40000").to_json(),
            Number.from_value("0").to_json(),
        )

    # def test_rounding_to_nearest(self):
    #     """Test 'to_nearest' rounding behavior (round half to even / banker's rounding).

    #     Test cases ported from rippled's Number_test.cpp testRounding() method.
    #     """
    #     # Test cases: (mantissa, exponent, expected_rounded_integer)
    #     # These test the "to_nearest" rounding mode

    #     # Positive numbers
    #     test_cases = [
    #         (13, -1, 1),
    #         (23, -1, 2),
    #         # (1.5, expected=2) - round half to even (Banker's rounding)
    #         (15, -1, 2),
    #         (25, -1, 2),
    #         (152, -2, 2),
    #         (252, -2, 3),
    #         (17, -1, 2),
    #         (27, -1, 3),
    #         # Negative numbers
    #         (-13, -1, -1),
    #         (-23, -1, -2),
    #         # (-1.5, expected=-2) - round half to even
    #         (-15, -1, -2),
    #         # (-2.5, expected=-2) - round half to even
    #         (-25, -1, -2),
    #         (-152, -2, -2),
    #         (-252, -2, -3),
    #         (-17, -1, -2),
    #         (-27, -1, -3),
    #     ]

    #     for mantissa, exponent, expected in test_cases:
    #         num = Number.from_mantissa_exponent(mantissa, exponent)
    #         # result = num.round_to_integer()
    #         self.assertEqual(
    #             num,
    #             expected,
    #             f"Number({mantissa}, {exponent}) rounded to_nearest: "
    #             f"expected {expected}, got {num}",
    #         )

    def test_rounding_large_numbers(self):
        pass
