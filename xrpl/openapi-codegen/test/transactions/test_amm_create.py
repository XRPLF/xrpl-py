import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.amm_create import AMMCreate


class TestAMMCreate(unittest.TestCase):
    def test_tx_invalid_trading_fee_greater_than_max(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMCreate(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                amount="12345",
                amount2="12345",
                trading_fee=1001,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_trading_fee_less_than_min(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMCreate(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                amount="12345",
                amount2="12345",
                trading_fee=-1,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMCreate(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                amount="12345",
                amount2="12345",
                trading_fee=0,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = AMMCreate(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount="12345",
            amount2="12345",
            trading_fee=0,
        )
        self.assertTrue(tx.is_valid())
