from unittest import TestCase

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.nftoken_offer import NFToken
from xrpl.models.ledger_objects.nftoken_page import NFTokenPage


class TestNFTokenPage(TestCase):
    def test_nftoken_page(self):
        nftoken_page_json = {
            "Flags": 0,
            "LedgerEntryType": "NFTokenPage",
            "PreviousTxnID": "95C8761B22894E328646F7A70035E9DFBECC9"
            "0EDD83E43B7B973F626D21A0822",
            "PreviousTxnLgrSeq": 42891441,
            "NFTokens": [
                {
                    "nftoken_id": "000B013A95F14B0044F78A264E41713"
                    "C64B5F89242540EE208C3098E00000D65",
                    "uri": "697066733A2F2F62616679626569676479727A74357366703775646D376"
                    "8753736"
                    "7568377932366E6634646675796C71616266336F636C67747179353566627A64"
                    "69",
                },
            ],
            "index": "",
        }
        actual = LedgerObject.from_xrpl(nftoken_page_json)
        expected = NFTokenPage(
            index="",
            previous_txn_id="95C8761B22894E328646F7A70035E9DFBEC"
            "C90EDD83E43B7B973F626D21A0822",
            previous_txn_lgr_seq=42891441,
            nftokens=[
                NFToken(
                    nftoken_id="000B013A95F14B0044F78A264E41713"
                    "C64B5F89242540EE208C3098E00000D65",
                    uri="697066733A2F2F62616679626569676479727A"
                    "74357366703775646D37687537367568377932366E"
                    "6634646675796C71616266336F636C67747179353566627A6469",
                )
            ],
        )
        self.assertEqual(actual, expected)
