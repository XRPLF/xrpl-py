import unittest

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.account_set_transaction import AccountSetTransaction

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestAccountSetTransaction(unittest.TestCase):
    def test_set_flag_and_clear_flag(self):
        set_flag = 3
        clear_flag = 3
        domain = "asjcsodafsaid0f9asdfasdf"
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "set_flag": set_flag,
            "clear_flag": clear_flag,
            "domain": domain,
            "sequence": _SEQUENCE,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)

    def test_uppercase_domain(self):
        clear_flag = 3
        domain = "asjcsodAOIJFsaid0f9asdfasdf"
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "clear_flag": clear_flag,
            "domain": domain,
            "sequence": _SEQUENCE,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)

    def test_invalid_tick_size(self):
        clear_flag = 3
        tick_size = 39
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "clear_flag": clear_flag,
            "tick_size": tick_size,
            "sequence": _SEQUENCE,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)

    def test_invalid_transfer_rate(self):
        clear_flag = 3
        transfer_rate = 39
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "clear_flag": clear_flag,
            "transfer_rate": transfer_rate,
            "sequence": _SEQUENCE,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)
