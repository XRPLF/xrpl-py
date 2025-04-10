import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.payment_channel_claim import PaymentChannelClaim
from xrpl.models.transactions.payment_channel_claim import PaymentChannelClaimFlag

class TestPaymentChannelClaim(unittest.TestCase):
    def test_tx_invalid_missing_required_param_channel(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelClaim(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="AAAAA",
               balance="AAAAA",
               credential_ids=[
                   "AAAAA"
               ],
               flags=PaymentChannelClaimFlag.TF_CLOSE,
               public_key="AAAAA",
               signature="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_credential_ids_less_than_min_items(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelClaim(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="AAAAA",
               balance="AAAAA",
               channel="AAAAA",
               credential_ids=[
               ],
               flags=PaymentChannelClaimFlag.TF_CLOSE,
               public_key="AAAAA",
               signature="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_credential_ids_more_than_max_items(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelClaim(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="AAAAA",
               balance="AAAAA",
               channel="AAAAA",
               credential_ids=[
                   "AAAAA",
                   "BBBBB",
                   "CCCCC",
                   "DDDDD",
                   "EEEEE",
                   "FFFFF",
                   "GGGGG",
                   "HHHHH",
                   "IIIII"
               ],
               flags=PaymentChannelClaimFlag.TF_CLOSE,
               public_key="AAAAA",
               signature="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelClaim(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               amount="AAAAA",
               balance="AAAAA",
               channel="AAAAA",
               credential_ids=[
                   "AAAAA"
               ],
               flags=PaymentChannelClaimFlag.TF_CLOSE,
               public_key="AAAAA",
               signature="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = PaymentChannelClaim(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount="AAAAA",
            balance="AAAAA",
            channel="AAAAA",
            credential_ids=[
                "AAAAA"
            ],
            flags=PaymentChannelClaimFlag.TF_CLOSE,
            public_key="AAAAA",
            signature="AAAAA"
        )
        self.assertTrue(tx.is_valid())
