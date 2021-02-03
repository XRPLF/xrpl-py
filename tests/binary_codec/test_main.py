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
    def test_simple(self):
        encoded = encode(TX_JSON)
        decoded = decode(encoded)
        self.assertEqual(TX_JSON, decoded)
