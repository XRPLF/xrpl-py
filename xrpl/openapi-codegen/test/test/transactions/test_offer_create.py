import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.offer_create import OfferCreate
from xrpl.models.transactions.offer_create import OfferCreateFlag

class TestOfferCreate(unittest.TestCase):
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            OfferCreate(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               expiration=5,
               flags=OfferCreateFlag.TF_FILL_OR_KILL,
               offer_sequence=5,
               taker_gets="12345",
               taker_pays="12345"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = OfferCreate(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            expiration=5,
            flags=OfferCreateFlag.TF_FILL_OR_KILL,
            offer_sequence=5,
            taker_gets="12345",
            taker_pays="12345"
        )
        self.assertTrue(tx.is_valid())
