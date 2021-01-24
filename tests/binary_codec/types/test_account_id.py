import unittest

from xrpl.binary_codec.types.account_id import AccountID

HEX_ENCODING = "5E7B112523F68D2F5E879DB4EAC51C6698A69304"
BASE58_ENCODING = "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"


class TestAccountID(unittest.TestCase):
    def test_from_value_hex(self):
        account_id = AccountID.from_value(HEX_ENCODING)
        self.assertEqual(account_id.to_json(), BASE58_ENCODING)

    def test_from_value_base58(self):
        account_id = AccountID.from_value(BASE58_ENCODING)
        self.assertEqual(account_id.to_hex(), HEX_ENCODING)
