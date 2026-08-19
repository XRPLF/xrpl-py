import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.escrow_cancel import EscrowCancel


class TestEscrowCancel(unittest.TestCase):
    def test_tx_invalid_missing_required_param_owner(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowCancel(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", offer_sequence=5)
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowCancel(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                offer_sequence=5,
                owner="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = EscrowCancel(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            offer_sequence=5,
            owner="AAAAA",
        )
        self.assertTrue(tx.is_valid())
