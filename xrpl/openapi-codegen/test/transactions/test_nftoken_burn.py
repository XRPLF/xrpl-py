import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.nftoken_burn import NFTokenBurn


class TestNFTokenBurn(unittest.TestCase):
    def test_tx_invalid_missing_required_param_nftoken_id(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenBurn(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", owner="AAAAA")
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenBurn(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                nftoken_id="AAAAA",
                owner="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = NFTokenBurn(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            nftoken_id="AAAAA",
            owner="AAAAA",
        )
        self.assertTrue(tx.is_valid())
