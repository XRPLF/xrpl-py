import unittest

from xrpl.models import AccountSet, Simulate
from xrpl.models.exceptions import XRPLModelException
from xrpl.transaction import sign
from xrpl.wallet import Wallet

_WALLET = Wallet.create()
_TRANSACTION = AccountSet(account=_WALLET.address, sequence=1)


class TestSimulate(unittest.TestCase):
    def test_simulate_with_both_tx_blob_and_transaction(self):
        with self.assertRaises(XRPLModelException) as e:
            Simulate(
                tx_blob=_TRANSACTION.blob(),
                transaction=_TRANSACTION,
            )
        self.assertEqual(
            e.exception.args[0],
            "{'tx': 'Must have exactly one of `tx_blob` and `transaction` fields.'}",
        )

    def test_simulate_with_neither_tx_blob_nor_transaction(self):
        with self.assertRaises(XRPLModelException) as e:
            Simulate()
        self.assertEqual(
            e.exception.args[0],
            "{'tx': 'Must have exactly one of `tx_blob` and `transaction` fields.'}",
        )

    def test_simulate_with_signed_transaction(self):
        signed_tx = sign(_TRANSACTION, _WALLET)
        with self.assertRaises(XRPLModelException) as e:
            Simulate(transaction=signed_tx)
        self.assertEqual(
            e.exception.args[0],
            "{'transaction': 'Cannot simulate a signed transaction.'}",
        )

    def test_simulate_with_valid_tx_blob(self):
        tx_blob = _TRANSACTION.blob()
        simulate = Simulate(tx_blob=tx_blob)
        self.assertEqual(simulate.tx_blob, tx_blob)
        self.assertIsNone(simulate.transaction)
        self.assertIsNone(simulate.binary)
        self.assertEqual(simulate.method, "simulate")
        self.assertTrue(simulate.is_valid())

    def test_simulate_with_valid_transaction(self):
        simulate = Simulate(transaction=_TRANSACTION)
        self.assertIsNone(simulate.tx_blob)
        self.assertEqual(simulate.transaction, _TRANSACTION)
        self.assertIsNone(simulate.binary)
        self.assertEqual(simulate.method, "simulate")
        self.assertTrue(simulate.is_valid())

    def test_simulate_with_binary(self):
        tx_blob = _TRANSACTION.blob()
        simulate = Simulate(tx_blob=tx_blob, binary=True)
        self.assertEqual(simulate.tx_blob, tx_blob)
        self.assertIsNone(simulate.transaction)
        self.assertTrue(simulate.binary)
        self.assertEqual(simulate.method, "simulate")
        self.assertTrue(simulate.is_valid())
