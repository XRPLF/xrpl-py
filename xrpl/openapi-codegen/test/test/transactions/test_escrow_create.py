import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.escrow_create import EscrowCreate

class TestEscrowCreate(unittest.TestCase):
    def test_tx_invalid_missing_required_param_amount(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowCreate(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               cancel_after=5,
               condition="AAAAA",
               destination="AAAAA",
               destination_tag=5,
               finish_after=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_finish_after_larger_than_cancel_after(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowCreate(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="AAAAA",
               cancel_after=5,
               condition="AAAAA",
               destination="AAAAA",
               destination_tag=5,
               finish_after=6
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowCreate(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               amount="AAAAA",
               cancel_after=5,
               condition="AAAAA",
               destination="AAAAA",
               destination_tag=5,
               finish_after=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = EscrowCreate(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount="AAAAA",
            cancel_after=5,
            condition="AAAAA",
            destination="AAAAA",
            destination_tag=5,
            finish_after=5
        )
        self.assertTrue(tx.is_valid())
