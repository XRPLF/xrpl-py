import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.xchain_commit import Currency
from xrpl.models.transactions.xchain_commit import XChainBridge
from xrpl.models.transactions.xchain_commit import XChainCommit

class TestXChainCommit(unittest.TestCase):
    def test_tx_invalid_missing_required_param_issuing_chain_door(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainCommit(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="12345",
               other_chain_destination="AAAAA",
               xchain_bridge=XChainBridge(
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               ),
               xchain_claim_id="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_missing_required_param_amount(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainCommit(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               other_chain_destination="AAAAA",
               xchain_bridge=XChainBridge(
                   issuing_chain_door="AAAAA",
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               ),
               xchain_claim_id="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainCommit(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               amount="12345",
               other_chain_destination="AAAAA",
               xchain_bridge=XChainBridge(
                   issuing_chain_door="AAAAA",
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               ),
               xchain_claim_id="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_issuer_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainCommit(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="12345",
               other_chain_destination="AAAAA",
               xchain_bridge=XChainBridge(
                   issuing_chain_door="AAAAA",
                   issuing_chain_issue=Currency(currency="USD", issuer="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE")
               ),
               xchain_claim_id="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = XChainCommit(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount="12345",
            other_chain_destination="AAAAA",
            xchain_bridge=XChainBridge(
                issuing_chain_door="AAAAA",
                issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                locking_chain_door="AAAAA",
                locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
            ),
            xchain_claim_id="AAAAA"
        )
        self.assertTrue(tx.is_valid())
