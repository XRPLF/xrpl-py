import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.trust_set import TrustSet
from xrpl.models.transactions.trust_set import TrustSetFlag

class TestTrustSet(unittest.TestCase):
    def test_tx_invalid_missing_required_param_limit_amount(self):
        with self.assertRaises(XRPLModelException) as err:
            TrustSet(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               flags=TrustSetFlag.TF_CLEAR_FREEZE,
               quality_in=5,
               quality_out=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            TrustSet(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               flags=TrustSetFlag.TF_CLEAR_FREEZE,
               limit_amount="12345",
               quality_in=5,
               quality_out=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = TrustSet(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            flags=TrustSetFlag.TF_CLEAR_FREEZE,
            limit_amount="12345",
            quality_in=5,
            quality_out=5
        )
        self.assertTrue(tx.is_valid())
