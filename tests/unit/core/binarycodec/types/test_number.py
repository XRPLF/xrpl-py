import unittest

from xrpl.core.binarycodec.types.number import Number


class TestNumber(unittest.TestCase):
    def test_serialization_and_deserialization(self):
        number_bytes = Number.from_value(124)
        self.assertEqual(Number(number_bytes).to_json(), "124")
