import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.xchain_add_claim_attestation import Currency
from xrpl.models.transactions.xchain_add_claim_attestation import XChainAddClaimAttestation
from xrpl.models.transactions.xchain_add_claim_attestation import XChainBridge

class TestXChainAddClaimAttestation(unittest.TestCase):
    def test_tx_invalid_missing_required_param_amount(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainAddClaimAttestation(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               attestation_reward_account="AAAAA",
               attestation_signer_account="AAAAA",
               destination="AAAAA",
               other_chain_source="AAAAA",
               public_key="AAAAA",
               signature="AAAAA",
               was_locking_chain_send=5,
               xchain_bridge=XChainBridge(
                   issuing_chain_door="AAAAA",
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               ),
               xchain_claim_id="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_missing_required_param_issuing_chain_door(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainAddClaimAttestation(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="AAAAA",
               attestation_reward_account="AAAAA",
               attestation_signer_account="AAAAA",
               destination="AAAAA",
               other_chain_source="AAAAA",
               public_key="AAAAA",
               signature="AAAAA",
               was_locking_chain_send=5,
               xchain_bridge=XChainBridge(
                   issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                   locking_chain_door="AAAAA",
                   locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
               ),
               xchain_claim_id="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            XChainAddClaimAttestation(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               amount="AAAAA",
               attestation_reward_account="AAAAA",
               attestation_signer_account="AAAAA",
               destination="AAAAA",
               other_chain_source="AAAAA",
               public_key="AAAAA",
               signature="AAAAA",
               was_locking_chain_send=5,
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
            XChainAddClaimAttestation(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               amount="AAAAA",
               attestation_reward_account="AAAAA",
               attestation_signer_account="AAAAA",
               destination="AAAAA",
               other_chain_source="AAAAA",
               public_key="AAAAA",
               signature="AAAAA",
               was_locking_chain_send=5,
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
        tx = XChainAddClaimAttestation(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount="AAAAA",
            attestation_reward_account="AAAAA",
            attestation_signer_account="AAAAA",
            destination="AAAAA",
            other_chain_source="AAAAA",
            public_key="AAAAA",
            signature="AAAAA",
            was_locking_chain_send=5,
            xchain_bridge=XChainBridge(
                issuing_chain_door="AAAAA",
                issuing_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"),
                locking_chain_door="AAAAA",
                locking_chain_issue=Currency(currency="USD", issuer="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
            ),
            xchain_claim_id="AAAAA"
        )
        self.assertTrue(tx.is_valid())
