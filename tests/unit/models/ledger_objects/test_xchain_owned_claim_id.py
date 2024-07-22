from unittest import TestCase

from xrpl.models.currencies.xrp import XRP
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.xchain_owned_claim_id import (
    XChainClaimProofSig,
    XChainOwnedClaimID,
)
from xrpl.models.xchain_bridge import XChainBridge


class TestXChainOwnedClaimID(TestCase):
    def test_xchain_owned_claim_id(self):
        xchain_owned_claim_id_json = {
            "Account": "rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
            "Flags": 0,
            "OtherChainSource": "r9oXrvBX5aDoyMGkoYvzazxDhYoWFUjz8p",
            "OwnerNode": "0",
            "PreviousTxnID": "1CFD80E9CF232B8EED62A52857DE97438D12230C0"
            "6496932A81DEFA6E660"
            "70A6",
            "PreviousTxnLgrSeq": 58673,
            "SignatureReward": "100",
            "XChainBridge": {
                "IssuingChainDoor": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                "IssuingChainIssue": {"currency": "XRP"},
                "LockingChainDoor": "rMAXACCrp3Y8PpswXcg3bKggHX76V3F8M4",
                "LockingChainIssue": {"currency": "XRP"},
            },
            "XChainClaimAttestations": [
                {
                    "XChainClaimProofSig": {
                        "Amount": "1000000",
                        "AttestationRewardAccount": "rfgjrgEJGDxfUY2U8VEDs7BnB1jiH3of"
                        "u6",
                        "AttestationSignerAccount": "rfsxNxZ6xB1nTPhTMwQajNnkCxWG8B71"
                        "4n",
                        "Destination": "rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                        "PublicKey": "025CA526EF20567A50FEC504589F949E0E3401C13EF76DD"
                        "5FD1CC285"
                        "0FA485BD7B",
                        "WasLockingChainSend": 1,
                    }
                },
                {
                    "XChainClaimProofSig": {
                        "Amount": "1000000",
                        "AttestationRewardAccount": "rUUL1tP523M8KimERqVS7sxb1tLLmpnd"
                        "yv",
                        "AttestationSignerAccount": "rEg5sHxZVTNwRL3BAdMwJatkmWDzHMmz"
                        "DF",
                        "Destination": "rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                        "PublicKey": "03D40434A6843638681E2F215310EBC4131AFB12EA85985"
                        "DA073183B"
                        "732525F7C9",
                        "WasLockingChainSend": 1,
                    },
                },
            ],
            "XChainClaimID": "b5",
            "LedgerEntryType": "XChainOwnedClaimID",
            "LedgerIndex": "20B136D7BF6D2E3D610E28E3E6BE09F5C8F4F0241BBF6E2D072AE1BAC"
            "B1388F5",
        }
        actual = LedgerObject.from_xrpl(xchain_owned_claim_id_json)
        expected = XChainOwnedClaimID(
            account="rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
            other_chain_source="r9oXrvBX5aDoyMGkoYvzazxDhYoWFUjz8p",
            owner_node="0",
            previous_txn_id="1CFD80E9CF232B8EED62A52857DE97438D12230C06496932A81DEFA6E6"
            "6070A6",
            previous_txn_lgr_seq=58673,
            signature_reward="100",
            xchain_bridge=XChainBridge(
                issuing_chain_door="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                issuing_chain_issue=XRP(),
                locking_chain_door="rMAXACCrp3Y8PpswXcg3bKggHX76V3F8M4",
                locking_chain_issue=XRP(),
            ),
            xchain_claim_attestations=[
                XChainClaimProofSig(
                    amount="1000000",
                    attestation_reward_account="rfgjrgEJGDxfUY2U8VEDs7BnB1jiH3ofu6",
                    attestation_signer_account="rfsxNxZ6xB1nTPhTMwQajNnkCxWG8B714n",
                    destination="rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                    public_key="025CA526EF20567A50FEC504589F949E0E3401C13EF76DD5FD1CC2"
                    "850FA485BD7B",
                    was_locking_chain_send=1,
                ),
                XChainClaimProofSig(
                    amount="1000000",
                    attestation_reward_account="rUUL1tP523M8KimERqVS7sxb1tLLmpndyv",
                    attestation_signer_account="rEg5sHxZVTNwRL3BAdMwJatkmWDzHMmzDF",
                    destination="rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                    public_key="03D40434A6843638681E2F215310EBC4131AFB12EA85985DA07318"
                    "3B732525F7C9",
                    was_locking_chain_send=1,
                ),
            ],
            xchain_claim_id="b5",
            ledger_index="20B136D7BF6D2E3D610E28E3E6BE09F5C8F4F0241BBF6E2D072AE1BACB13"
            "88F5",
        )
        self.assertEqual(actual, expected)
