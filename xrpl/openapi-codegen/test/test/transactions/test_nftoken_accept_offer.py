import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.nftoken_accept_offer import NFTokenAcceptOffer

class TestNFTokenAcceptOffer(unittest.TestCase):
    def test_tx_invalid_missing_required_param_account(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenAcceptOffer(
               nftoken_broker_fee="12345",
               nftoken_buy_offer="AAAAA",
               nftoken_sell_offer="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_dependent_presence_missing_nftoken_buy_offer(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenAcceptOffer(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               nftoken_broker_fee="12345",
               nftoken_sell_offer="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_require_one_of_missing_nftoken_sell_offer_nftoken_buy_offer(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenAcceptOffer(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               nftoken_broker_fee="12345"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_nftoken_broker_fee_not_greater_than_0(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenAcceptOffer(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               nftoken_broker_fee="0",
               nftoken_buy_offer="AAAAA",
               nftoken_sell_offer="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            NFTokenAcceptOffer(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               nftoken_broker_fee="12345",
               nftoken_buy_offer="AAAAA",
               nftoken_sell_offer="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = NFTokenAcceptOffer(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            nftoken_broker_fee="12345",
            nftoken_buy_offer="AAAAA",
            nftoken_sell_offer="AAAAA"
        )
        self.assertTrue(tx.is_valid())
