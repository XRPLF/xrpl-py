import unittest

from xrpl.core.binarycodec.types.number import Number


class TestNumber(unittest.TestCase):
    def test_serialization_and_deserialization(self):
        number_bytes = Number.from_value(124)
        self.assertEqual((number_bytes).to_json(), "124.0")

        number_bytes = Number.from_value(0)
        self.assertEqual((number_bytes).to_json(), "0.0")

        number_bytes = Number.from_value(-10)
        self.assertEqual((number_bytes).to_json(), "-10.0")
