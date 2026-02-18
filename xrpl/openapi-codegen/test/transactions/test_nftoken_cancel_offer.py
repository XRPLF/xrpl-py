import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.nftoken_cancel_offer import NFTokenCancelOffer


class TestNFTokenCancelOffer(unittest.TestCase):
    def test_tx_invalid_missing_required_param_nftoken_offers(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenCancelOffer(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_nftoken_offers_less_than_min_items(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenCancelOffer(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", nftoken_offers=[]
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenCancelOffer(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE", nftoken_offers=["AAAAA"]
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = NFTokenCancelOffer(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", nftoken_offers=["AAAAA"]
        )
        self.assertTrue(tx.is_valid())
