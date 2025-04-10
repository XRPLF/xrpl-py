import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.set_regular_key import SetRegularKey


class TestSetRegularKey(unittest.TestCase):
    def test_tx_invalid_missing_required_param_account(self):
        with self.assertRaises(XRPLModelException) as err:
            SetRegularKey(regular_key="AAAAA")
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            SetRegularKey(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE", regular_key="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = SetRegularKey(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", regular_key="AAAAA"
        )
        self.assertTrue(tx.is_valid())
