from unittest import TestCase

from xrpl.models.ledger_objects.did import DID
from xrpl.models.ledger_objects.ledger_object import LedgerObject


class TestDID(TestCase):
    def test_did(self):
        did_json = {
            "Account": "rpfqJrXg5uidNo2ZsRhRY6TiF1cvYmV9Fg",
            "DIDDocument": "646F63",
            "Data": "617474657374",
            "Flags": 0,
            "LedgerEntryType": "DID",
            "OwnerNode": "0",
            "PreviousTxnID": "A4C15DA185E6092DF5954FF62A1446220C61A5F60F0D93B4B0"
            "9F708778E41120",
            "PreviousTxnLgrSeq": 4,
            "URI": "6469645F6578616D706C65",
            "index": "46813BE38B798B3752CA590D44E7FEADB17485649074403AD1761A2835CE91FF",
        }
        actual = LedgerObject.from_xrpl(did_json)
        expected = DID(
            account="rpfqJrXg5uidNo2ZsRhRY6TiF1cvYmV9Fg",
            did_document="646F63",
            data="617474657374",
            owner_node="0",
            previous_txn_id="A4C15DA185E6092DF5954FF62A1446220C61A5F60F0D93B4B09F"
            "708778E41120",
            previous_txn_lgr_seq=4,
            uri="6469645F6578616D706C65",
            index="46813BE38B798B3752CA590D44E7FEADB17485649074403AD1761A2835CE91FF",
        )
        self.assertEqual(actual, expected)
