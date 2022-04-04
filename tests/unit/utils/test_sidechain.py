from unittest import TestCase

import xrpl.utils
from xrpl.constants import XRPLException
from xrpl.models import Memo, Payment

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
_AMOUNT = "10"

_SIDECHAIN_DEST = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_EXPECTED_MEMO = Memo(memo_data=xrpl.utils.str_to_hex(_SIDECHAIN_DEST))


class TestSidechain(TestCase):
    def test_create_cross_chain_payment_successful(self):
        payment = Payment(account=_ACCOUNT, amount=_AMOUNT, destination=_DESTINATION)

        result = xrpl.utils.create_cross_chain_payment(payment, _SIDECHAIN_DEST)
        expected = Payment(
            account=_ACCOUNT,
            amount=_AMOUNT,
            destination=_DESTINATION,
            memos=[_EXPECTED_MEMO],
        )

        self.assertEqual(result, expected)

    def test_create_cross_chain_payment_successful_memos(self):
        memo = Memo(memo_data="deadbeef")
        payment = Payment(
            account=_ACCOUNT, amount=_AMOUNT, destination=_DESTINATION, memos=[memo]
        )

        result = xrpl.utils.create_cross_chain_payment(payment, _SIDECHAIN_DEST)
        expected = Payment(
            account=_ACCOUNT,
            amount=_AMOUNT,
            destination=_DESTINATION,
            memos=[_EXPECTED_MEMO, memo],
        )

        self.assertEqual(result, expected)

    def test_create_cross_chain_payment_remove_txnsignature(self):
        payment = Payment(
            account=_ACCOUNT,
            amount=_AMOUNT,
            destination=_DESTINATION,
            txn_signature="oaisudofiasd",
        )

        result = xrpl.utils.create_cross_chain_payment(payment, _SIDECHAIN_DEST)
        expected = Payment(
            account=_ACCOUNT,
            amount=_AMOUNT,
            destination=_DESTINATION,
            memos=[_EXPECTED_MEMO],
        )

        self.assertEqual(result, expected)

    def test_create_cross_chain_payment_too_many_memos(self):
        memo = Memo(memo_data="deadbeef")
        payment = Payment(
            account=_ACCOUNT, amount=_AMOUNT, destination=_DESTINATION, memos=[memo] * 3
        )

        with self.assertRaises(XRPLException):
            xrpl.utils.create_cross_chain_payment(payment, _SIDECHAIN_DEST)
