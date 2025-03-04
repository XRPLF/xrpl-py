import unittest

from xrpl.core.binarycodec.types.number import Number


class TestNumber(unittest.TestCase):
    def test_serialization_and_deserialization(self):
        serialized_number = Number.from_value("124")
        self.assertEqual(serialized_number.to_json(), "1240000000000000e-13")

        serialized_number = Number.from_value("1000")
        self.assertEqual(serialized_number.to_json(), "1000000000000000e-12")

        serialized_number = Number.from_value("0")
        self.assertEqual(serialized_number.to_json(), "0")

        serialized_number = Number.from_value("-1")
        self.assertEqual(serialized_number.to_json(), "-1000000000000000e-15")

        serialized_number = Number.from_value("-10")
        self.assertEqual(serialized_number.to_json(), "-1000000000000000e-14")

        serialized_number = Number.from_value("123.456")
        self.assertEqual(serialized_number.to_json(), "1234560000000000e-13")

        serialized_number = Number.from_value("1.456e-45")
        self.assertEqual(serialized_number.to_json(), "1456000000000000e-60")

        serialized_number = Number.from_value("0.456e34")
        self.assertEqual(serialized_number.to_json(), "4560000000000000e18")

        serialized_number = Number.from_value("4e34")
        self.assertEqual(serialized_number.to_json(), "4000000000000000e19")

    def extreme_limits(self):
        pass
