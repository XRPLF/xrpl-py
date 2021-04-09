from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.transaction import Transaction, TransactionType

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestTransaction(TestCase):
    def test_missing_required_field(self):
        with self.assertRaises(XRPLModelException):
            # missing account
            Transaction(
                fee=_FEE,
                sequence=_SEQUENCE,
                transaction_type=TransactionType.ACCOUNT_DELETE,
            )

    def test_initializes_if_all_required_fields_present(self):
        tx = Transaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            transaction_type=TransactionType.ACCOUNT_DELETE,
        )
        self.assertTrue(tx.is_valid())

    def test_to_dict_includes_type_as_string(self):
        tx = Transaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            transaction_type=TransactionType.ACCOUNT_DELETE,
        )
        value = tx.to_dict()["transaction_type"]
        self.assertEqual(type(value), str)

    def test_to_dict_flag_list(self):
        tx = Transaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            transaction_type=TransactionType.ACCOUNT_DELETE,
            flags=[0b1, 0b10, 0b100],
        )
        expected_flags = 0b111
        value = tx.to_dict()["flags"]
        self.assertEqual(value, expected_flags)
