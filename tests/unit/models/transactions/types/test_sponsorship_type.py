"""Unit tests for SponsorshipType enum."""

from unittest import TestCase

from xrpl.models.transactions.types import SponsorshipType


class TestSponsorshipType(TestCase):
    """Tests for SponsorshipType enum."""

    def test_fee_value(self):
        """Test that FEE has correct value."""
        self.assertEqual(SponsorshipType.FEE, 0x00000001)
        self.assertEqual(SponsorshipType.FEE.value, 1)

    def test_reserve_value(self):
        """Test that RESERVE has correct value."""
        self.assertEqual(SponsorshipType.RESERVE, 0x00000002)
        self.assertEqual(SponsorshipType.RESERVE.value, 2)

    def test_enum_members(self):
        """Test that enum has exactly 2 members."""
        members = list(SponsorshipType)
        self.assertEqual(len(members), 2)
        self.assertIn(SponsorshipType.FEE, members)
        self.assertIn(SponsorshipType.RESERVE, members)

    def test_enum_is_int(self):
        """Test that SponsorshipType is an int enum."""
        self.assertIsInstance(SponsorshipType.FEE.value, int)
        self.assertIsInstance(SponsorshipType.RESERVE.value, int)

    def test_bitwise_operations(self):
        """Test that enum values can be used in bitwise operations."""
        # Test combining flags
        combined = SponsorshipType.FEE.value | SponsorshipType.RESERVE.value
        self.assertEqual(combined, 3)

        # Test checking individual flags
        self.assertTrue(combined & SponsorshipType.FEE.value)
        self.assertTrue(combined & SponsorshipType.RESERVE.value)

    def test_enum_name_access(self):
        """Test accessing enum by name."""
        self.assertEqual(SponsorshipType["FEE"], SponsorshipType.FEE)
        self.assertEqual(SponsorshipType["RESERVE"], SponsorshipType.RESERVE)

    def test_enum_value_access(self):
        """Test accessing enum by value."""
        self.assertEqual(SponsorshipType(1), SponsorshipType.FEE)
        self.assertEqual(SponsorshipType(2), SponsorshipType.RESERVE)

