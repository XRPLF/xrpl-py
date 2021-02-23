from unittest import TestCase

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.transaction import Transaction, TransactionType

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
                transaction_type=TransactionType.AccountDelete,
            )

    def test_initializes_if_all_required_fields_present(self):
        tx = Transaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            transaction_type=TransactionType.AccountDelete,
        )
        self.assertTrue(tx.is_valid())

    def test_to_dict_includes_type_as_string(self):
        tx = Transaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            transaction_type=TransactionType.AccountDelete,
        )
        value = tx.to_dict()["transaction_type"]
        self.assertEqual(type(value), str)
