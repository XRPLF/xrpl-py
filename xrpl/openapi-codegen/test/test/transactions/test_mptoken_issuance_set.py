import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.mptoken_issuance_set import MPTokenIssuanceSet
from xrpl.models.transactions.mptoken_issuance_set import MPTokenIssuanceSetFlag


class TestMPTokenIssuanceSet(unittest.TestCase):
    def test_tx_invalid_missing_required_param_mptoken_issuance_id(self):
        with self.assertRaises(XRPLModelException) as err:
            MPTokenIssuanceSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
                holder="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            MPTokenIssuanceSet(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
                holder="AAAAA",
                mptoken_issuance_id="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = MPTokenIssuanceSet(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
            holder="AAAAA",
            mptoken_issuance_id="AAAAA",
        )
        self.assertTrue(tx.is_valid())
