from unittest import TestCase

from xrpl.models.ledger_objects.check import Check
from xrpl.models.ledger_objects.ledger_object import LedgerObject


class TestCheck(TestCase):
    def test_check(self):
        check_json = {
            "Account": "rUn84CUYbNjRoTQ6mSW7BVJPSVJNLb1QLo",
            "Destination": "rfkE1aSy9G8Upk4JssnwBxhEv5p4mn2KTy",
            "DestinationNode": "0000000000000000",
            "DestinationTag": 1,
            "Expiration": 570113521,
            "Flags": 0,
            "InvoiceID": "46060241FABCF692D4D934BA2A6C4427CD4279083E3"
            "8C77CBE642243E43BE291",
            "LedgerEntryType": "Check",
            "OwnerNode": "0000000000000000",
            "PreviousTxnID": "5463C6E08862A1FAE5EDAC12D70ADB16546A1F67"
            "4930521295BC082494B62924",
            "PreviousTxnLgrSeq": 6,
            "SendMax": "100000000",
            "Sequence": 2,
            "index": "49647F0D748DC3FE26BDACBC57F251AADEFFF391403EC9BF87C97F67E9977FB0",
        }
        actual = LedgerObject.from_xrpl(check_json)
        expected = Check(
            index="49647F0D748DC3FE26BDACBC57F251AADEFFF391403EC9BF87C97F67E9977FB0",
            account="rUn84CUYbNjRoTQ6mSW7BVJPSVJNLb1QLo",
            destination="rfkE1aSy9G8Upk4JssnwBxhEv5p4mn2KTy",
            owner_node="0000000000000000",
            previous_txn_id="5463C6E08862A1FAE5EDAC12D70ADB16546A"
            "1F674930521295BC082494B62924",
            previous_txn_lgr_seq=6,
            send_max="100000000",
            sequence=2,
            destination_node="0000000000000000",
            destination_tag=1,
            expiration=570113521,
            invoice_id="46060241FABCF692D4D934BA2A6C4427CD427"
            "9083E38C77CBE642243E43BE291",
        )
        self.assertEqual(actual, expected)
