from unittest import TestCase

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.pay_channel import PayChannel


class TestPayChannel(TestCase):
    def test_pay_channel(self):
        pay_channel_json = {
            "Account": "rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
            "Destination": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            "Amount": "4325800",
            "Balance": "2323423",
            "PublicKey": "32D2471DB72B27E3310F355BB33E339BF26F8392D5A93D3BC0FC3B566612D"
            "A0F0A",
            "SettleDelay": 3600,
            "Expiration": 536027313,
            "CancelAfter": 536891313,
            "SourceTag": 0,
            "DestinationTag": 1002341,
            "DestinationNode": "0000000000000000",
            "Flags": 0,
            "LedgerEntryType": "PayChannel",
            "OwnerNode": "0000000000000000",
            "PreviousTxnID": "F0AB71E777B2DA54B86231E19B82554E"
            "F1F8211F92ECA473121C655BFC5329BF",
            "PreviousTxnLgrSeq": 14524914,
            "index": "96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
        }
        actual = LedgerObject.from_xrpl(pay_channel_json)
        expected = PayChannel(
            index="96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
            account="rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
            amount="4325800",
            balance="2323423",
            destination="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            flags=0,
            owner_node="0000000000000000",
            public_key="32D2471DB72B27E3310F355BB33E339BF26F83"
            "92D5A93D3BC0FC3B566612DA0F0A",
            previous_txn_id="F0AB71E777B2DA54B86231E19B82554EF1"
            "F8211F92ECA473121C655BFC5329BF",
            previous_txn_lgr_seq=14524914,
            settle_delay=3600,
            destination_node="0000000000000000",
            destination_tag=1002341,
            expiration=536027313,
            cancel_after=536891313,
            source_tag=0,
        )
        self.assertEqual(actual, expected)
