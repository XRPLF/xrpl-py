from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.check_cash import CheckCash

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_CHECK_ID = "838766BA2B995C00744175F69A1B11E32C3DBC40E64801A4056FCBD657F57334"
_AMOUNT = "300"


class TestCheckCash(TestCase):
    def test_amount_and_deliver_min_is_invalid(self):
        with self.assertRaises(XRPLModelException):
            CheckCash(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                check_id=_CHECK_ID,
                amount=_AMOUNT,
                deliver_min=_AMOUNT,
            )

    def test_neither_amount_not_deliver_min_is_invalid(self):
        with self.assertRaises(XRPLModelException):
            CheckCash(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                check_id=_CHECK_ID,
            )

    def test_amount_without_deliver_min_is_valid(self):
        tx = CheckCash(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            check_id=_CHECK_ID,
            amount=_AMOUNT,
        )
        self.assertTrue(tx.is_valid())

    def test_deliver_min_without_amount_is_valid(self):
        tx = CheckCash(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            check_id=_CHECK_ID,
            deliver_min=_AMOUNT,
        )
        self.assertTrue(tx.is_valid())
