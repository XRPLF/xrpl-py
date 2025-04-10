import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.amm_delete import AMMDelete
from xrpl.models.transactions.amm_delete import Currency

class TestAMMDelete(unittest.TestCase):
    def test_tx_invalid_missing_required_param_asset(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMDelete(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               asset2=Currency(
                   currency="USD",
                   issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMDelete(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               asset=Currency(
                   currency="USD",
                   issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
               ),
               asset2=Currency(
                   currency="USD",
                   issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_issuer_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMDelete(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               asset=Currency(
                   currency="USD",
                   issuer="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"
               ),
               asset2=Currency(
                   currency="USD",
                   issuer="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = AMMDelete(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            asset=Currency(
                currency="USD",
                issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
            ),
            asset2=Currency(
                currency="USD",
                issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
            )
        )
        self.assertTrue(tx.is_valid())
