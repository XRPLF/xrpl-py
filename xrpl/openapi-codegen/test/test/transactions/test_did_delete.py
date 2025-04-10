import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.did_delete import DIDDelete

class TestDIDDelete(unittest.TestCase):
    def test_tx_invalid_missing_required_param_account(self):
        with self.assertRaises(XRPLModelException) as err:
            DIDDelete(
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            DIDDelete(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = DIDDelete(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        )
        self.assertTrue(tx.is_valid())
