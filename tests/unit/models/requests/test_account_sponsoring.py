from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import AccountSponsoring


class TestAccountSponsoring(TestCase):
    def test_valid_account_sponsoring(self):
        """Test valid AccountSponsoring request with required field."""
        req = AccountSponsoring(account="rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk")
        self.assertTrue(req.is_valid())
        self.assertEqual(req.account, "rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk")

    def test_account_sponsoring_with_ledger_index(self):
        """Test AccountSponsoring with ledger_index."""
        req = AccountSponsoring(
            account="rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk", ledger_index="validated"
        )
        self.assertTrue(req.is_valid())
        self.assertEqual(req.ledger_index, "validated")

    def test_account_sponsoring_with_ledger_hash(self):
        """Test AccountSponsoring with ledger_hash."""
        req = AccountSponsoring(
            account="rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk",
            ledger_hash="ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789",
        )
        self.assertTrue(req.is_valid())
        self.assertEqual(
            req.ledger_hash,
            "ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789",
        )

    def test_account_sponsoring_with_limit(self):
        """Test AccountSponsoring with limit."""
        req = AccountSponsoring(account="rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk", limit=10)
        self.assertTrue(req.is_valid())
        self.assertEqual(req.limit, 10)

    def test_account_sponsoring_with_marker(self):
        """Test AccountSponsoring with marker for pagination."""
        req = AccountSponsoring(
            account="rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk",
            marker="some_marker_value",
        )
        self.assertTrue(req.is_valid())
        self.assertEqual(req.marker, "some_marker_value")

    def test_account_sponsoring_with_all_fields(self):
        """Test AccountSponsoring with all optional fields."""
        req = AccountSponsoring(
            account="rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk",
            ledger_index="validated",
            limit=20,
            marker="marker123",
        )
        self.assertTrue(req.is_valid())
        self.assertEqual(req.account, "rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk")
        self.assertEqual(req.ledger_index, "validated")
        self.assertEqual(req.limit, 20)
        self.assertEqual(req.marker, "marker123")

    def test_account_sponsoring_missing_account(self):
        """Test that AccountSponsoring requires account field."""
        with self.assertRaises(XRPLModelException):
            AccountSponsoring()

    def test_account_sponsoring_to_dict(self):
        """Test AccountSponsoring serialization to dict."""
        req = AccountSponsoring(
            account="rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk", limit=10
        )
        req_dict = req.to_dict()
        self.assertEqual(req_dict["account"], "rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk")
        self.assertEqual(req_dict["limit"], 10)
        self.assertEqual(req_dict["method"], "account_sponsoring")

