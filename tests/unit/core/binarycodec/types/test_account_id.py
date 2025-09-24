from unittest import TestCase

from xrpl.core.binarycodec import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.account_id import AccountID

HEX_ENCODING = "5E7B112523F68D2F5E879DB4EAC51C6698A69304"
BASE58_ENCODING = "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"


class TestAccountID(TestCase):
    def test_from_value_hex(self):
        account_id = AccountID.from_value(HEX_ENCODING)
        self.assertEqual(account_id.to_json(), BASE58_ENCODING)

    def test_from_value_base58(self):
        account_id = AccountID.from_value(BASE58_ENCODING)
        # Note that I converted the hex to uppercase here...
        # We may want to decide if we want the implemention of `to_hex` in
        # SerializedType to return uppercase hex by default.
        self.assertEqual(account_id.to_hex(), HEX_ENCODING)

    def test_raises_invalid_value_type(self):
        invalid_value = 30
        self.assertRaises(XRPLBinaryCodecException, AccountID.from_value, invalid_value)

    def test_special_account_ACCOUNT_ONE(self):
        self.assertEqual(
            AccountID.from_value("0000000000000000000000000000000000000001").to_json(),
            "rrrrrrrrrrrrrrrrrrrrBZbvji",
        )

        self.assertEqual(
            AccountID.from_value("rrrrrrrrrrrrrrrrrrrrBZbvji").to_hex(),
            AccountID.from_value("0000000000000000000000000000000000000001").to_hex(),
        )

    def test_special_account_ACCOUNT_ZERO(self):
        self.assertEqual(
            AccountID.from_value("0000000000000000000000000000000000000000").to_json(),
            "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
        )

        self.assertEqual(
            AccountID.from_value("rrrrrrrrrrrrrrrrrrrrrhoLvTp").to_hex(),
            AccountID.from_value("0000000000000000000000000000000000000000").to_hex(),
        )
