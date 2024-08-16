from unittest import TestCase

from xrpl.models.currencies.xrp import XRP
from xrpl.models.ledger_objects.bridge import Bridge
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.xchain_bridge import XChainBridge


class TestBridge(TestCase):
    def test_bridge(self):
        bridge_json = {
            "Account": "r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
            "Flags": 0,
            "LedgerEntryType": "Bridge",
            "MinAccountCreateAmount": "2000000000",
            "OwnerNode": "0",
            "PreviousTxnID": "67A8A1B36C1B97BE3AAB6B19CB3A3069034877DE"
            "917FD1A71919EAE7548E56"
            "36",
            "PreviousTxnLgrSeq": 102,
            "SignatureReward": "204",
            "XChainAccountClaimCount": "0",
            "XChainAccountCreateCount": "0",
            "XChainBridge": {
                "IssuingChainDoor": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                "IssuingChainIssue": {"currency": "XRP"},
                "LockingChainDoor": "r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
                "LockingChainIssue": {"currency": "XRP"},
            },
            "XChainClaimID": "1",
            "index": "9F2C9E23343852036AFD323025A8506018ABF9D4DBAA746D61BF1CFB5C297D10",
        }
        actual = LedgerObject.from_xrpl(bridge_json)
        expected = Bridge(
            account="r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
            min_account_create_amount="2000000000",
            owner_node="0",
            previous_txn_id="67A8A1B36C1B97BE3AAB6B19CB3A3069034877DE917FD1A71919EAE75"
            "48E5636",
            previous_txn_lgr_seq=102,
            signature_reward="204",
            xchain_account_claim_count="0",
            xchain_account_create_count="0",
            xchain_bridge=XChainBridge(
                issuing_chain_door="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                issuing_chain_issue=XRP(),
                locking_chain_door="r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
                locking_chain_issue=XRP(),
            ),
            xchain_claim_id="1",
            index="9F2C9E23343852036AFD323025A8506018ABF9D4DBAA746D61BF1CFB5C297D10",
        )
        self.assertEqual(actual, expected)
