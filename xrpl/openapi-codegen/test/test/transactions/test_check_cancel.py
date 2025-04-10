import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.check_cancel import CheckCancel


class TestCheckCancel(unittest.TestCase):
    def test_tx_invalid_missing_required_param_check_id(self):
        with self.assertRaises(XRPLModelException) as err:
            CheckCancel(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            CheckCancel(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                check_id="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = CheckCancel(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            check_id="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
        )
        self.assertTrue(tx.is_valid())
