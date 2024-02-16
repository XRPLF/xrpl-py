from unittest import TestCase

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.signer_list import SignerList
from xrpl.models.transactions.signer_list_set import SignerEntry


class TestSignerList(TestCase):
    def test_signer_list(self):
        signer_list_json = {
            "Flags": 0,
            "LedgerEntryType": "SignerList",
            "OwnerNode": "0000000000000000",
            "PreviousTxnID": "5904C0DC72C58A83AEFED2FFC5386356"
            "AA83FCA6A88C89D00646E51E687CDBE4",
            "PreviousTxnLgrSeq": 16061435,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                        "SignerWeight": 2,
                    }
                },
                {
                    "SignerEntry": {
                        "Account": "raKEEVSGnKSD9Zyvxu4z6Pqpm4ABH8FS6n",
                        "SignerWeight": 1,
                    }
                },
                {
                    "SignerEntry": {
                        "Account": "rUpy3eEg8rqjqfUoLeBnZkscbKbFsKXC3v",
                        "SignerWeight": 1,
                    }
                },
            ],
            "SignerListID": 0,
            "SignerQuorum": 3,
            "index": "A9C28A28B85CD533217F5C0A0C7767666B093FA58A0F2D80026FCC4CD932DDC7",
        }
        actual = LedgerObject.from_xrpl(signer_list_json)
        expected = SignerList(
            index="A9C28A28B85CD533217F5C0A0C7767666B093FA58A0F2D80026FCC4CD932DDC7",
            flags=0,
            owner_node="0000000000000000",
            previous_txn_id="5904C0DC72C58A83AEFED2FFC5386356"
            "AA83FCA6A88C89D00646E51E687CDBE4",
            previous_txn_lgr_seq=16061435,
            signer_entries=[
                SignerEntry(
                    account="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                    signer_weight=2,
                ),
                SignerEntry(
                    account="raKEEVSGnKSD9Zyvxu4z6Pqpm4ABH8FS6n",
                    signer_weight=1,
                ),
                SignerEntry(
                    account="rUpy3eEg8rqjqfUoLeBnZkscbKbFsKXC3v",
                    signer_weight=1,
                ),
            ],
            signer_list_id=0,
            signer_quorum=3,
        )
        self.assertEqual(actual, expected)
