import unittest

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.clawback import Clawback


class TestClawback(unittest.TestCase):
    def test_tx_invalid_missing_required_param_amount(self):
        with self.assertRaises(XRPLModelException) as err:
            Clawback(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", holder="AAAAA")
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_value_not_numeric(self):
        with self.assertRaises(XRPLModelException) as err:
            Clawback(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                amount=IssuedCurrencyAmount(
                    currency="USD",
                    issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                    value="AAAAA",
                ),
                holder="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            Clawback(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                amount=IssuedCurrencyAmount(
                    currency="USD",
                    issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                    value="12345",
                ),
                holder="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_issuer_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            Clawback(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                amount=IssuedCurrencyAmount(
                    currency="USD",
                    issuer="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                    value="12345",
                ),
                holder="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = Clawback(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount=IssuedCurrencyAmount(
                currency="USD",
                issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                value="12345",
            ),
            holder="AAAAA",
        )
        self.assertTrue(tx.is_valid())
