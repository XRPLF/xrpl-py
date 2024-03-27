from unittest import TestCase

from xrpl.models.ledger_objects.escrow import Escrow
from xrpl.models.ledger_objects.ledger_object import LedgerObject


class TestEscrow(TestCase):
    def test_escrow(self):
        escrow_json = {
            "Account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            "Amount": "10000",
            "CancelAfter": 545440232,
            "Condition": "A0258020A82A88B2DF843A54F58772E4A386"
            "1866ECDB4157645DD9AE528C1D3AEEDAB"
            "AB6810120",
            "Destination": "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX",
            "DestinationTag": 23480,
            "FinishAfter": 545354132,
            "Flags": 0,
            "LedgerEntryType": "Escrow",
            "OwnerNode": "0000000000000000",
            "DestinationNode": "0000000000000000",
            "PreviousTxnID": "C44F2EB84196B9AD820313DBEBA6316A15C9A2"
            "D35787579ED172B87A30131DA7",
            "PreviousTxnLgrSeq": 28991004,
            "SourceTag": 11747,
            "index": "DC5F3851D8A1AB622F957761E5963BC5BD439D5C24AC6AD7AC4523F0640244AC",
        }
        actual = LedgerObject.from_xrpl(escrow_json)
        expected = Escrow(
            index="DC5F3851D8A1AB622F957761E5963BC5BD439D5C24AC6AD7AC4523F0640244AC",
            account="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            amount="10000",
            destination="ra5nK24KXen9AHvsdFTKHSANinZseWnPcX",
            owner_node="0000000000000000",
            previous_txn_id="C44F2EB84196B9AD820313DBEBA6316A15"
            "C9A2D35787579ED172B87A30131DA7",
            previous_txn_lgr_seq=28991004,
            condition="A0258020A82A88B2DF843A54F58772E4A3861866EC"
            "DB4157645DD9AE528C1D3AEEDABAB6810120",
            cancel_after=545440232,
            destination_node="0000000000000000",
            destination_tag=23480,
            finish_after=545354132,
            source_tag=11747,
        )
        self.assertEqual(actual, expected)
