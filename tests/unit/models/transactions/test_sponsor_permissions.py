"""Tests for sponsor-related granular permissions."""

from unittest import TestCase

from xrpl.models.transactions.delegate_set import GranularPermission


class TestSponsorGranularPermissions(TestCase):
    def test_sponsor_fee_permission_exists(self):
        """Verify SponsorFee granular permission exists."""
        self.assertEqual(GranularPermission.SPONSOR_FEE, "SponsorFee")

    def test_sponsor_reserve_permission_exists(self):
        """Verify SponsorReserve granular permission exists."""
        self.assertEqual(GranularPermission.SPONSOR_RESERVE, "SponsorReserve")
