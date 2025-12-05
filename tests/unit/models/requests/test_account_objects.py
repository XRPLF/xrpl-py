from unittest import TestCase

from xrpl.models.requests import AccountObjects
from xrpl.models.requests.account_objects import AccountObjectType


class TestAccountObjects(TestCase):
    def test_type_with_enum(self):
        """Test that AccountObjects accepts AccountObjectType enum for type field."""
        req = AccountObjects(
            account="rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9",
            type=AccountObjectType.ESCROW,
        )
        self.assertEqual(req.type, AccountObjectType.ESCROW)

    def test_type_with_canonical_string(self):
        """Test that AccountObjects accepts canonical ledger entry name string."""
        req = AccountObjects(
            account="rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9",
            type="Escrow",
        )
        self.assertEqual(req.type, "Escrow")

    def test_type_with_lowercase_string(self):
        """Test that AccountObjects accepts lowercase string (same as enum value)."""
        req = AccountObjects(
            account="rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9",
            type="escrow",
        )
        self.assertEqual(req.type, "escrow")

    def test_to_dict_with_string_type(self):
        """Test that to_dict() works correctly with string type."""
        req = AccountObjects(
            account="rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9",
            type="Escrow",
        )
        result = req.to_dict()
        self.assertEqual(result["type"], "Escrow")

    def test_to_dict_with_enum_type(self):
        """Test that to_dict() works correctly with enum type."""
        req = AccountObjects(
            account="rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9",
            type=AccountObjectType.ESCROW,
        )
        result = req.to_dict()
        self.assertEqual(result["type"], "escrow")
