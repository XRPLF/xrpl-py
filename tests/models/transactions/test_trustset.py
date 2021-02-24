from unittest import TestCase

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions import TrustSet

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_XRP_AMOUNT = "10000"


class TestTrustSet(TestCase):
    def test_trustset_invalid_limit_amount(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            # limit_amount must be an issued currency amount
            "limit_amount": _XRP_AMOUNT,
        }
        with self.assertRaises(XRPLModelValidationException):
            TrustSet(**transaction_dict)
