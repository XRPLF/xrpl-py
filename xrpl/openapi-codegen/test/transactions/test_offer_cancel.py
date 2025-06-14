import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.offer_cancel import OfferCancel


class TestOfferCancel(unittest.TestCase):
    def test_tx_invalid_missing_required_param_offer_sequence(self):
        with self.assertRaises(XRPLModelException) as err:
            OfferCancel(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            OfferCancel(account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE", offer_sequence=5)
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = OfferCancel(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", offer_sequence=5)
        self.assertTrue(tx.is_valid())
