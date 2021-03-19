from unittest import TestCase

from xrpl.core.binarycodec import XRPLBinaryCodecException
from xrpl.core.binarycodec.binary_wrappers import BinaryParser
from xrpl.core.binarycodec.types.vector256 import Vector256

HASH1 = "42426C4D4F1009EE67080A9B7965B44656D7714D104A72F9B4369F97ABF044EE"
HASH2 = "4C97EBA926031A7CF7D7B36FDE3ED66DDA5421192D63DE53FFB46E43B9DC8373"
HASH_LIST = [HASH1, HASH2]
SERIALIZED = HASH1 + HASH2


class TestVector256(TestCase):
    def test_from_value(self):
        vector256_object = Vector256.from_value(HASH_LIST)
        self.assertEqual(vector256_object.to_hex(), SERIALIZED)

    def test_from_parser(self):
        parser = BinaryParser(SERIALIZED)
        vector256_object = Vector256.from_parser(parser)
        self.assertEqual(vector256_object.to_hex(), SERIALIZED)

    def test_to_json(self):
        vector256_object = Vector256.from_value(HASH_LIST)
        self.assertEqual(vector256_object.to_json(), HASH_LIST)

    def test_raises_invalid_value_type(self):
        invalid_value = 1
        self.assertRaises(XRPLBinaryCodecException, Vector256.from_value, invalid_value)
