from unittest import TestCase

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.offer import Offer


class TestOffer(TestCase):
    def test_offer(self):
        offer_json = {
            "Account": "rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
            "BookDirectory": "ACC27DE91DBA86FC509069EAF4BC511D7"
            "3128B780F2E54BF5E07A369E2446000",
            "BookNode": "0000000000000000",
            "Flags": 131072,
            "LedgerEntryType": "Offer",
            "OwnerNode": "0000000000000000",
            "PreviousTxnID": "F0AB71E777B2DA54B86231E19B82554EF1"
            "F8211F92ECA473121C655BFC5329BF",
            "PreviousTxnLgrSeq": 14524914,
            "Sequence": 866,
            "TakerGets": {
                "currency": "XAG",
                "issuer": "r9Dr5xwkeLegBeXq6ujinjSBLQzQ1zQGjH",
                "value": "37",
            },
            "TakerPays": "79550000000",
            "index": "96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
        }
        actual = LedgerObject.from_xrpl(offer_json)
        expected = Offer(
            index="96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
            account="rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
            taker_gets=IssuedCurrencyAmount(
                currency="XAG", issuer="r9Dr5xwkeLegBeXq6ujinjSBLQzQ1zQGjH", value="37"
            ),
            taker_pays="79550000000",
            sequence=866,
            flags=131072,
            book_directory="ACC27DE91DBA86FC509069EAF4BC511D7"
            "3128B780F2E54BF5E07A369E2446000",
            book_node="0000000000000000",
            owner_node="0000000000000000",
            previous_txn_id="F0AB71E777B2DA54B86231E19B82554EF1F821"
            "1F92ECA473121C655BFC5329BF",
            previous_txn_lgr_seq=14524914,
        )
        self.assertEqual(actual, expected)
