import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.xchain_create_bridge import Currency
from xrpl.models.transactions.xchain_create_bridge import XChainBridge
from xrpl.models.transactions.xchain_create_bridge import XChainCreateBridge

class TestXChainCreateBridge(unittest.TestCase):
    def test_tx_invalid_missing_required_param_issuing_chain_door(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainCreateBridge(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               min_account_create_amount="12345",
               signature_reward="12345",
               xchain_bridge=XChainBridge(
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainCreateBridge(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               min_account_create_amount="12345",
               signature_reward="12345",
               xchain_bridge=XChainBridge(
                   issuing_chain_door="AAAAA",
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_issuer_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainCreateBridge(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               min_account_create_amount="12345",
               signature_reward="12345",
               xchain_bridge=XChainBridge(
                   issuing_chain_door="AAAAA",
                   issuing_chain_issue=Currency(currency="USD", issuer="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE")
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = XChainCreateBridge(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            min_account_create_amount="12345",
            signature_reward="12345",
            xchain_bridge=XChainBridge(
                issuing_chain_door="AAAAA",
                issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                locking_chain_door="AAAAA",
                locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
            )
        )
        self.assertTrue(tx.is_valid())
