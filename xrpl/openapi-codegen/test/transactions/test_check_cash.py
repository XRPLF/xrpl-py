import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.check_cash import CheckCash


class TestCheckCash(unittest.TestCase):
    def test_tx_invalid_missing_required_param_check_id(self):
        with self.assertRaises(XRPLModelException) as err:
            CheckCash(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                amount="12345",
                deliver_min="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_both_amount_deliver_min_present(self):
        with self.assertRaises(XRPLModelException) as err:
            CheckCash(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                amount="12345",
                check_id="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                deliver_min="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            CheckCash(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                amount="12345",
                check_id="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                deliver_min="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = CheckCash(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount="12345",
            check_id="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            deliver_min="12345",
        )
        self.assertTrue(tx.is_valid())
