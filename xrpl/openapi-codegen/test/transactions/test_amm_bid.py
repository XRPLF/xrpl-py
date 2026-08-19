import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.amm_bid import AMMBid
from xrpl.models.transactions.amm_bid import AuthAccount
from xrpl.models.transactions.amm_bid import Currency


class TestAMMBid(unittest.TestCase):
    def test_tx_invalid_missing_required_param_asset(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMBid(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                asset2=Currency(
                    currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
                ),
                auth_accounts=[
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                ],
                bid_max="12345",
                bid_min="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_missing_required_param_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMBid(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                asset=Currency(
                    currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
                ),
                asset2=Currency(
                    currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
                ),
                auth_accounts=[
                    AuthAccount(),
                    AuthAccount(),
                    AuthAccount(),
                    AuthAccount(),
                ],
                bid_max="12345",
                bid_min="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMBid(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                asset=Currency(
                    currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
                ),
                asset2=Currency(
                    currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
                ),
                auth_accounts=[
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                ],
                bid_max="12345",
                bid_min="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMBid(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                asset=Currency(
                    currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
                ),
                asset2=Currency(
                    currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
                ),
                auth_accounts=[
                    AuthAccount(account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"),
                    AuthAccount(account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"),
                    AuthAccount(account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"),
                    AuthAccount(account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"),
                ],
                bid_max="12345",
                bid_min="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_issuer_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AMMBid(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                asset=Currency(
                    currency="USD", issuer="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"
                ),
                asset2=Currency(
                    currency="USD", issuer="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"
                ),
                auth_accounts=[
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                    AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                ],
                bid_max="12345",
                bid_min="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = AMMBid(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            asset=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
            asset2=Currency(
                currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
            ),
            auth_accounts=[
                AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                AuthAccount(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
            ],
            bid_max="12345",
            bid_min="12345",
        )
        self.assertTrue(tx.is_valid())
