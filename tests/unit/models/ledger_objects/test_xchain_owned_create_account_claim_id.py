from unittest import TestCase

from xrpl.models.currencies.xrp import XRP
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.xchain_owned_create_account_claim_id import (
    XChainCreateAccountProofSig,
    XChainOwnedCreateAccountClaimID,
)
from xrpl.models.xchain_bridge import XChainBridge


class TestXChainOwnedCreateAccountClaimID(TestCase):
    def test_xchain_owned_create_account_claim_id(self):
        xchain_owned_create_account_claim_id_json = {
            "Flags": 0,
            "LedgerEntryType": "XChainOwnedCreateAccountClaimID",
            "LedgerIndex": "5A92F6ED33FDA68FB4B9FD140EA38C056CD2BA9673ECA5B4CEF40F2166B"
            "B6F0C",
            "OwnerNode": "0",
            "PreviousTxnID": "1CFD80E9CF232B8EED62A52857DE97438D12230C06496932A81DEFA6"
            "E660",
            "PreviousTxnLgrSeq": 58673,
            "Account": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            "XChainAccountCreateCount": "66",
            "XChainBridge": {
                "IssuingChainDoor": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                "IssuingChainIssue": {"currency": "XRP"},
                "LockingChainDoor": "rMAXACCrp3Y8PpswXcg3bKggHX76V3F8M4",
                "LockingChainIssue": {"currency": "XRP"},
            },
            "XChainCreateAccountAttestations": [
                {
                    "XChainCreateAccountProofSig": {
                        "Amount": "20000000",
                        "AttestationRewardAccount": "rMtYb1vNdeMDpD9tA5qSFm8WXEBdEo"
                        "KKVw",
                        "AttestationSignerAccount": "rL8qTrAvZ8Q1o1H9H9Ahpj3xjgmRvF"
                        "LvJ3",
                        "Destination": "rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                        "PublicKey": "021F7CC4033EFBE5E8214B04D1BAAEC14808DC6C02F4A"
                        "CE930A8"
                        "EF0F5909B0C438",
                        "SignatureReward": "100",
                        "WasLockingChainSend": 1,
                    }
                }
            ],
        }
        actual = LedgerObject.from_xrpl(xchain_owned_create_account_claim_id_json)
        expected = XChainOwnedCreateAccountClaimID(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            owner_node="0",
            previous_txn_id="1CFD80E9CF232B8EED62A52857DE97438D12230C06496932A81D"
            "EFA6E660",
            previous_txn_lgr_seq=58673,
            ledger_index="5A92F6ED33FDA68FB4B9FD140EA38C056CD2BA9673ECA5B4CEF40F2166B"
            "B6F0C",
            xchain_account_create_count="66",
            xchain_bridge=XChainBridge(
                issuing_chain_door="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                issuing_chain_issue=XRP(),
                locking_chain_door="rMAXACCrp3Y8PpswXcg3bKggHX76V3F8M4",
                locking_chain_issue=XRP(),
            ),
            xchain_create_account_attestations=[
                XChainCreateAccountProofSig(
                    amount="20000000",
                    attestation_reward_account="rMtYb1vNdeMDpD9tA5qSFm8WXEBdEoKKVw",
                    attestation_signer_account="rL8qTrAvZ8Q1o1H9H9Ahpj3xjgmRvFLvJ3",
                    destination="rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                    public_key="021F7CC4033EFBE5E8214B04D1BAAEC14808DC6C02F4ACE930A8E"
                    "F0F5909B0C438",
                    signature_reward="100",
                    was_locking_chain_send=1,
                )
            ],
        )
        self.assertEqual(actual, expected)
