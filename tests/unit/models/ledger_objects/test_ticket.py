from unittest import TestCase

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.ticket import Ticket


class TestTicket(TestCase):
    def test_ticket(self):
        ticket_json = {
            "Account": "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
            "Flags": 0,
            "LedgerEntryType": "Ticket",
            "OwnerNode": "0000000000000000",
            "PreviousTxnID": "F19AD4577212D3BEACA0F75FE1BA1"
            "644F2E854D46E8D62E9C95D18E9708CBFB1",
            "PreviousTxnLgrSeq": 4,
            "TicketSequence": 3,
            "index": "A9C28A28B85CD533217F5C0A0C7767666B093FA58A0F2D80026FCC4CD932DDC7",
        }
        actual = LedgerObject.from_xrpl(ticket_json)
        expected = Ticket(
            index="A9C28A28B85CD533217F5C0A0C7767666B093FA58A0F2D80026FCC4CD932DDC7",
            account="rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
            flags=0,
            owner_node="0000000000000000",
            previous_txn_id="F19AD4577212D3BEACA0F75FE1BA1644F2E85"
            "4D46E8D62E9C95D18E9708CBFB1",
            previous_txn_lgr_seq=4,
            ticket_sequence=3,
        )
        self.assertEqual(actual, expected)
