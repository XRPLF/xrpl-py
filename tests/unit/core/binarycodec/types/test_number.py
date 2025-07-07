import unittest

from xrpl.core.binarycodec.types.number import Number


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

        serialized_number = Number.from_value("-10")
        self.assertEqual(serialized_number.to_json(), "-10")

        serialized_number = Number.from_value("123.456")
        self.assertEqual(serialized_number.to_json(), "123.456")

        serialized_number = Number.from_value("1.456e-45")
        self.assertEqual(serialized_number.to_json(), "1456000000000000e-60")

        serialized_number = Number.from_value("0.456e34")
        self.assertEqual(serialized_number.to_json(), "4560000000000000e18")

        serialized_number = Number.from_value("4e34")
        self.assertEqual(serialized_number.to_json(), "4000000000000000e19")

    def test_extreme_limits(self):
        lowest_mantissa = "-9223372036854776"
        serialized_number = Number.from_value(lowest_mantissa + "e3")
        self.assertEqual(
            serialized_number.display_serialized_hex(), "FFDF3B645A1CAC0800000003"
        )

        highest_mantissa = "9223372036854776"
        serialized_number = Number.from_value(highest_mantissa + "e3")
        self.assertEqual(
            serialized_number.display_serialized_hex(), "0020C49BA5E353F800000003"
        )
