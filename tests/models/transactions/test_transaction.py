from unittest import TestCase

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.transaction import Transaction

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestTransaction(TestCase):
    def test_missing_required_field(self):
        with self.assertRaises(XRPLModelValidationException):
            # missing account
            Transaction(
                fee=_FEE,
                sequence=_SEQUENCE,
            )

    def test_initializes_if_all_required_fields_present(self):
        tx = Transaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
        )
        self.assertTrue(tx.is_valid())
