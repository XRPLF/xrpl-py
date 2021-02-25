from unittest import TestCase

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions import DepositPreauth


class TestDepositPreauth(TestCase):
    def test_authorize_deauthorize_both_set(self):
        authorize = "authorize"
        deauthorize = "deauthorize"

        transaction_dict = {
            "authorize": authorize,
            "deauthorize": deauthorize,
        }
        with self.assertRaises(XRPLModelValidationException):
            DepositPreauth.from_dict(transaction_dict)

    def test_authorize_deauthorize_neither_set(self):
        transaction_dict = {}
        with self.assertRaises(XRPLModelValidationException):
            DepositPreauth.from_dict(transaction_dict)
