from unittest import TestCase

from xrpl.models.requests import AccountObjects
from xrpl.models.requests.account_objects import AccountObjectType
from xrpl.models.requests.ledger_entry import LedgerEntryType


class TestAccountObjects(TestCase):
    def test_type_with_account_object_type_enum(self):
        """Test that AccountObjects accepts AccountObjectType enum for type field."""
        req = AccountObjects(
            account="rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9",
            type=AccountObjectType.ESCROW,
        )
        self.assertEqual(req.type, AccountObjectType.ESCROW)

    def test_type_with_ledger_entry_type_enum(self):
        """Test that AccountObjects accepts LedgerEntryType enum for type field."""
        req = AccountObjects(
            account="rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9",
            type=LedgerEntryType.ESCROW,
        )
        self.assertEqual(req.type, LedgerEntryType.ESCROW)

    def test_to_dict_with_account_object_type(self):
        """Test that to_dict() works correctly with AccountObjectType enum."""
        req = AccountObjects(
            account="rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9",
            type=AccountObjectType.ESCROW,
        )
        result = req.to_dict()
        self.assertEqual(result["type"], "escrow")

    def test_to_dict_with_ledger_entry_type(self):
        """Test that to_dict() works correctly with LedgerEntryType enum."""
        req = AccountObjects(
            account="rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9",
            type=LedgerEntryType.ESCROW,
        )
        result = req.to_dict()
        self.assertEqual(result["type"], "escrow")
