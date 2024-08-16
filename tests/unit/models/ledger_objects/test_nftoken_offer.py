from unittest import TestCase

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.nftoken_offer import NFTokenOffer


class TestNFTokenOffer(TestCase):
    def test_nftoken_offer(self):
        nftoken_offer_json = {
            "LedgerEntryType": "NFTokenOffer",
            "index": "AEBABA4FAC212BF28E0F9A9C3788A47B085557EC5D1429E7A8266FB859C863B3",
            "Amount": "1000000",
            "Flags": 1,
            "NFTokenID": "00081B5825A08C22787716FA031B432EBBC1B101BB54875F0002D2A40000"
            "0000",
            "Owner": "rhRxL3MNvuKEjWjL7TBbZSDacb8PmzAd7m",
            "PreviousTxnID": "BFA9BE27383FA315651E26FDE1FA30815C5A5D0544EE10EC33D3E925"
            "32993"
            "769",
            "PreviousTxnLgrSeq": 75443565,
            "OwnerNode": "17",
            "NFTokenOfferNode": "0",
        }
        actual = LedgerObject.from_xrpl(nftoken_offer_json)
        expected = NFTokenOffer(
            index="AEBABA4FAC212BF28E0F9A9C3788A47B085557EC5D1429E7A8266FB859C863B3",
            amount="1000000",
            flags=1,
            nftoken_id="00081B5825A08C22787716FA031B432EBBC1B101BB54875F0002D2A400000"
            "000",
            owner="rhRxL3MNvuKEjWjL7TBbZSDacb8PmzAd7m",
            previous_txn_id="BFA9BE27383FA315651E26FDE1FA30815C5A5D0544EE10EC33D3E925"
            "32993769",
            previous_txn_lgr_seq=75443565,
            owner_node="17",
            nftoken_offer_node="0",
        )
        self.assertEqual(actual, expected)
