import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.payment_channel_fund import PaymentChannelFund

class TestPaymentChannelFund(unittest.TestCase):
    def test_tx_invalid_missing_required_param_channel(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelFund(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="1",
               expiration=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_amount_not_numeric(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelFund(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="AAAAA",
               channel="AAAAA",
               expiration=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_amount_not_greater_than_0(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelFund(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="0",
               channel="AAAAA",
               expiration=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelFund(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               amount="1",
               channel="AAAAA",
               expiration=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = PaymentChannelFund(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount="1",
            channel="AAAAA",
            expiration=5
        )
        self.assertTrue(tx.is_valid())
