import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.mptoken_authorize import MPTokenAuthorize
from xrpl.models.transactions.mptoken_authorize import MPTokenAuthorizeFlag

class TestMPTokenAuthorize(unittest.TestCase):
    def test_tx_invalid_missing_required_param_mptoken_issuance_id(self):
        with self.assertRaises(XRPLModelException) as err:
            MPTokenAuthorize(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               flags=MPTokenAuthorizeFlag.TF_MPT_UNAUTHORIZE,
               holder="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            MPTokenAuthorize(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               flags=MPTokenAuthorizeFlag.TF_MPT_UNAUTHORIZE,
               holder="AAAAA",
               mptoken_issuance_id="UNHANDLED_CASE"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = MPTokenAuthorize(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            flags=MPTokenAuthorizeFlag.TF_MPT_UNAUTHORIZE,
            holder="AAAAA",
            mptoken_issuance_id="UNHANDLED_CASE"
        )
        self.assertTrue(tx.is_valid())
