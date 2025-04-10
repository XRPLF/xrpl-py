import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.ticket_create import TicketCreate

class TestTicketCreate(unittest.TestCase):
    def test_tx_invalid_ticket_count_greater_than_max(self):
        with self.assertRaises(XRPLModelException) as err:
            TicketCreate(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               ticket_count=251
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_ticket_count_less_than_min(self):
        with self.assertRaises(XRPLModelException) as err:
            TicketCreate(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               ticket_count=0
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_missing_required_param_ticket_count(self):
        with self.assertRaises(XRPLModelException) as err:
            TicketCreate(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            TicketCreate(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               ticket_count=1
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = TicketCreate(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            ticket_count=1
        )
        self.assertTrue(tx.is_valid())
