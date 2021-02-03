import json
import os
import unittest

from xrpl.binary_codec.main import decode, encode

TX_JSON = {
    "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
    "Destination": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
    "Flags": (1 << 31),  # tfFullyCanonicalSig
    "Sequence": 1,
    "TransactionType": "Payment",
}


class TestMain(unittest.TestCase):
    maxDiff = 1000

    def test_simple(self):
        encoded = encode(TX_JSON)
        decoded = decode(encoded)
        self.assertEqual(TX_JSON, decoded)

    def test_codec_fixtures(self):
        dirname = os.path.dirname(__file__)
        filename = "fixtures/data/codec-fixtures.json"
        absolute_path = os.path.join(dirname, filename)
        with open(absolute_path) as data_driven_tests:
            fixtures_json = json.load(data_driven_tests)
            for test in fixtures_json["accountState"]:
                test_binary = test["binary"]
                test_json = test["json"]
                with self.subTest(test_binary=test_binary, test_json=test_json):
                    self.assertEqual(encode(test_json), test_binary)
                    self.assertEqual(decode(test_binary), test_json)
