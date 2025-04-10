import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.xchain_account_create_commit import Currency
from xrpl.models.transactions.xchain_account_create_commit import XChainAccountCreateCommit
from xrpl.models.transactions.xchain_account_create_commit import XChainBridge

class TestXChainAccountCreateCommit(unittest.TestCase):
    def test_tx_invalid_missing_required_param_issuing_chain_door(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainAccountCreateCommit(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="12345",
               destination="AAAAA",
               signature_reward="12345",
               xchain_bridge=XChainBridge(
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_missing_required_param_amount(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainAccountCreateCommit(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               destination="AAAAA",
               signature_reward="12345",
               xchain_bridge=XChainBridge(
                   issuing_chain_door="AAAAA",
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_amount_not_numeric(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainAccountCreateCommit(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="AAAAA",
               destination="AAAAA",
               signature_reward="12345",
               xchain_bridge=XChainBridge(
                   issuing_chain_door="AAAAA",
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_signature_reward_not_numeric(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainAccountCreateCommit(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="12345",
               destination="AAAAA",
               signature_reward="AAAAA",
               xchain_bridge=XChainBridge(
                   issuing_chain_door="AAAAA",
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               )
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainAccountCreateCommit(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               amount="12345",
               destination="AAAAA",
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
            XChainAccountCreateCommit(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="12345",
               destination="AAAAA",
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
        tx = XChainAccountCreateCommit(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount="12345",
            destination="AAAAA",
            signature_reward="12345",
            xchain_bridge=XChainBridge(
                issuing_chain_door="AAAAA",
                issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                locking_chain_door="AAAAA",
                locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
            )
        )
        self.assertTrue(tx.is_valid())
