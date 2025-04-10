import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.mptoken_issuance_create import MPTokenIssuanceCreate
from xrpl.models.transactions.mptoken_issuance_create import MPTokenIssuanceCreateFlag

class TestMPTokenIssuanceCreate(unittest.TestCase):
    def test_tx_invalid_missing_required_param_account(self):
        with self.assertRaises(XRPLModelException) as err:
            MPTokenIssuanceCreate(
               asset_scale=5,
               flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK,
               maximum_amount="AAAAA",
               mptoken_metadata="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_mptoken_metadata_too_short(self):
        with self.assertRaises(XRPLModelException) as err:
            MPTokenIssuanceCreate(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               asset_scale=5,
               flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK,
               maximum_amount="AAAAA",
               mptoken_metadata=""
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_present_transfer_fee_on_missing_tf_mpt_can_transfer(self):
        with self.assertRaises(XRPLModelException) as err:
            MPTokenIssuanceCreate(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               asset_scale=5,
               flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK,
               maximum_amount="AAAAA",
               mptoken_metadata="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               transfer_fee=0
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            MPTokenIssuanceCreate(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               asset_scale=5,
               flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK,
               maximum_amount="AAAAA",
               mptoken_metadata="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = MPTokenIssuanceCreate(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            asset_scale=5,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK,
            maximum_amount="AAAAA",
            mptoken_metadata="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a"
        )
        self.assertTrue(tx.is_valid())
