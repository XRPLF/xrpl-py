"""Unit tests for sponsorship-related GranularPermission additions."""

from unittest import TestCase

from xrpl.models.transactions import DelegateSet
from xrpl.models.transactions.delegate_set import GranularPermission, Permission


_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DELEGATED_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"


class TestGranularPermissionSponsorship(TestCase):
    """Tests for SPONSOR_FEE and SPONSOR_RESERVE granular permissions."""

    def test_sponsor_fee_exists(self):
        """Test that SPONSOR_FEE permission exists."""
        self.assertTrue(hasattr(GranularPermission, "SPONSOR_FEE"))
        self.assertEqual(GranularPermission.SPONSOR_FEE, "SponsorFee")

    def test_sponsor_reserve_exists(self):
        """Test that SPONSOR_RESERVE permission exists."""
        self.assertTrue(hasattr(GranularPermission, "SPONSOR_RESERVE"))
        self.assertEqual(GranularPermission.SPONSOR_RESERVE, "SponsorReserve")

    def test_sponsor_fee_in_delegate_set(self):
        """Test using SPONSOR_FEE in DelegateSet transaction."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_FEE),
            ],
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(
            tx.permissions[0].permission_value,
            GranularPermission.SPONSOR_FEE,
        )

    def test_sponsor_reserve_in_delegate_set(self):
        """Test using SPONSOR_RESERVE in DelegateSet transaction."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE),
            ],
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(
            tx.permissions[0].permission_value,
            GranularPermission.SPONSOR_RESERVE,
        )

    def test_both_sponsor_permissions_in_delegate_set(self):
        """Test using both SPONSOR_FEE and SPONSOR_RESERVE together."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_FEE),
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE),
            ],
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(len(tx.permissions), 2)
        permission_values = [p.permission_value for p in tx.permissions]
        self.assertIn(GranularPermission.SPONSOR_FEE, permission_values)
        self.assertIn(GranularPermission.SPONSOR_RESERVE, permission_values)

    def test_sponsor_permissions_with_other_permissions(self):
        """Test mixing sponsor permissions with other granular permissions."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_FEE),
                Permission(permission_value=GranularPermission.TRUSTLINE_AUTHORIZE),
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE),
                Permission(permission_value=GranularPermission.PAYMENT_MINT),
            ],
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(len(tx.permissions), 4)

    def test_sponsor_fee_string_value(self):
        """Test that SPONSOR_FEE has correct string value."""
        self.assertIsInstance(GranularPermission.SPONSOR_FEE.value, str)
        self.assertEqual(GranularPermission.SPONSOR_FEE.value, "SponsorFee")

    def test_sponsor_reserve_string_value(self):
        """Test that SPONSOR_RESERVE has correct string value."""
        self.assertIsInstance(GranularPermission.SPONSOR_RESERVE.value, str)
        self.assertEqual(GranularPermission.SPONSOR_RESERVE.value, "SponsorReserve")

    def test_all_granular_permissions_include_sponsor(self):
        """Test that sponsor permissions are in the complete enum."""
        all_permissions = list(GranularPermission)
        self.assertIn(GranularPermission.SPONSOR_FEE, all_permissions)
        self.assertIn(GranularPermission.SPONSOR_RESERVE, all_permissions)

    def test_enum_name_access(self):
        """Test accessing sponsor permissions by name."""
        self.assertEqual(
            GranularPermission["SPONSOR_FEE"],
            GranularPermission.SPONSOR_FEE,
        )
        self.assertEqual(
            GranularPermission["SPONSOR_RESERVE"],
            GranularPermission.SPONSOR_RESERVE,
        )

    def test_enum_value_access(self):
        """Test accessing sponsor permissions by value."""
        self.assertEqual(
            GranularPermission("SponsorFee"),
            GranularPermission.SPONSOR_FEE,
        )
        self.assertEqual(
            GranularPermission("SponsorReserve"),
            GranularPermission.SPONSOR_RESERVE,
        )

