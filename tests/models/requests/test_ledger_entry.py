from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import LedgerEntry
from xrpl.models.requests.ledger_entry import RippleState


class TestLedgerEntry(TestCase):
    def test_has_only_index_is_valid(self):
        req = LedgerEntry(
            index="hello",
        )
        self.assertTrue(req.is_valid())

    def test_has_only_account_root_is_valid(self):
        req = LedgerEntry(
            account_root="hello",
        )
        self.assertTrue(req.is_valid())

    def test_has_only_directory_is_valid(self):
        req = LedgerEntry(
            directory="hello",
        )
        self.assertTrue(req.is_valid())

    def test_has_only_offer_is_valid(self):
        req = LedgerEntry(
            offer="hello",
        )
        self.assertTrue(req.is_valid())

    def test_has_only_ripple_state_is_valid(self):
        req = LedgerEntry(
            ripple_state=RippleState(
                accounts=["account1", "account2"],
                currency="USD",
            ),
        )
        self.assertTrue(req.is_valid())

    def test_has_only_check_is_valid(self):
        req = LedgerEntry(
            check="hello",
        )
        self.assertTrue(req.is_valid())

    def test_has_only_escrow_is_valid(self):
        req = LedgerEntry(
            escrow="hello",
        )
        self.assertTrue(req.is_valid())

    def test_has_only_payment_channel_is_valid(self):
        req = LedgerEntry(
            payment_channel="hello",
        )
        self.assertTrue(req.is_valid())

    def test_has_only_deposit_preauth_is_valid(self):
        req = LedgerEntry(
            deposit_preauth="hello",
        )
        self.assertTrue(req.is_valid())

    def test_has_only_ticket_is_valid(self):
        req = LedgerEntry(
            ticket="hello",
        )
        self.assertTrue(req.is_valid())

    def test_has_no_query_param_is_invalid(self):
        with self.assertRaises(XRPLModelException):
            LedgerEntry()

    def test_has_multiple_query_params_is_invalid(self):
        with self.assertRaises(XRPLModelException):
            LedgerEntry(
                index="hello",
                account_root="hello",
            )
