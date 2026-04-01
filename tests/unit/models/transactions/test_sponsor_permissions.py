"""Tests for sponsor-related granular permissions."""

from unittest import TestCase

from xrpl.models.transactions.delegate_set import (
    DelegateSet,
    GranularPermission,
    Permission,
)

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_ACCOUNT2 = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"


class TestSponsorGranularPermissions(TestCase):
    # ------------------------------------------------------------------ #
    #  Enum identity (existing)                                           #
    # ------------------------------------------------------------------ #

    def test_sponsor_fee_permission_exists(self):
        """Verify SponsorFee granular permission exists."""
        self.assertEqual(GranularPermission.SPONSOR_FEE, "SponsorFee")

    def test_sponsor_reserve_permission_exists(self):
        """Verify SponsorReserve granular permission exists."""
        self.assertEqual(GranularPermission.SPONSOR_RESERVE, "SponsorReserve")

    # ------------------------------------------------------------------ #
    #  Serialization path — Permission nested model                       #
    # ------------------------------------------------------------------ #

    def test_permission_sponsor_fee_to_dict(self):
        """Permission wrapping SponsorFee serializes to the string value."""
        p = Permission(permission_value=GranularPermission.SPONSOR_FEE)
        # NestedModel wraps the fields under the lower-cased class name key
        d = p.to_dict()
        self.assertEqual(d["permission"]["permission_value"], "SponsorFee")

    def test_permission_sponsor_reserve_to_dict(self):
        """Permission wrapping SponsorReserve serializes to the string value."""
        p = Permission(permission_value=GranularPermission.SPONSOR_RESERVE)
        d = p.to_dict()
        self.assertEqual(d["permission"]["permission_value"], "SponsorReserve")

    def test_delegate_set_with_sponsor_fee_permission(self):
        """DelegateSet containing SponsorFee permission is valid and serializes."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_ACCOUNT2,
            permissions=[Permission(permission_value=GranularPermission.SPONSOR_FEE)],
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(
            d["permissions"][0]["permission"]["permission_value"], "SponsorFee"
        )

    def test_delegate_set_with_sponsor_reserve_permission(self):
        """DelegateSet containing SponsorReserve permission is valid and serializes."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_ACCOUNT2,
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE)
            ],
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(
            d["permissions"][0]["permission"]["permission_value"], "SponsorReserve"
        )

    def test_delegate_set_with_both_sponsor_permissions(self):
        """DelegateSet containing both sponsor permissions serializes correctly."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_ACCOUNT2,
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_FEE),
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE),
            ],
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        values = [p["permission"]["permission_value"] for p in d["permissions"]]
        self.assertIn("SponsorFee", values)
        self.assertIn("SponsorReserve", values)

    def test_delegate_set_to_xrpl_camel_case(self):
        """to_xrpl() emits CamelCase keys for sponsor permission DelegateSet."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_ACCOUNT2,
            permissions=[Permission(permission_value=GranularPermission.SPONSOR_FEE)],
        )
        xrpl_dict = tx.to_xrpl()
        self.assertIn("Permissions", xrpl_dict)
        self.assertIn("Authorize", xrpl_dict)
        # to_xrpl wraps nested Permission as {'Permission': {'PermissionValue': ...}}
        perm = xrpl_dict["Permissions"][0]
        self.assertIn("Permission", perm)
        self.assertEqual(perm["Permission"]["PermissionValue"], "SponsorFee")

    def test_delegate_set_from_dict_roundtrip_sponsor_fee(self):
        """Roundtrip through to_dict() / from_dict() preserves SponsorFee."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_ACCOUNT2,
            permissions=[Permission(permission_value=GranularPermission.SPONSOR_FEE)],
        )
        roundtripped = DelegateSet.from_dict(tx.to_dict())
        self.assertEqual(
            roundtripped.permissions[0].permission_value,
            GranularPermission.SPONSOR_FEE,
        )
