from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import DepositPreauth

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestDepositPreauth(TestCase):
    def test_authorize_unauthorize_both_set(self):
        with self.assertRaises(XRPLModelException):
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                authorize="authorize",
                unauthorize="unauthorize",
            )

    def test_authorize_unauthorize_neither_set(self):
        with self.assertRaises(XRPLModelException):
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
            )
