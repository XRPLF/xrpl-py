"""Unit tests for Sponsorship ledger entry."""

from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.ledger_objects import LedgerEntryType, Sponsorship, SponsorshipFlag

_OWNER = "rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk"
_SPONSEE = "rfkDkFai4jUfCvAJiZ5Vm7XvvWjYvDqeYo"
_OWNER_NODE = "0000000000000000"
_SPONSEE_NODE = "0000000000000000"
_PREVIOUS_TXN_ID = "1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF"
_PREVIOUS_TXN_LGR_SEQ = 12345678
_INDEX = "ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789"


class TestSponsorship(TestCase):
    """Tests for Sponsorship ledger entry."""

    def test_valid_sponsorship_with_fee_amount(self):
        """Test creating a valid Sponsorship with fee_amount."""
        sponsorship = Sponsorship(
            owner=_OWNER,
            sponsee=_SPONSEE,
            owner_node=_OWNER_NODE,
            sponsee_node=_SPONSEE_NODE,
            fee_amount="1000000",  # 1 XRP
            max_fee="1000",
            flags=0,
        )
        self.assertTrue(sponsorship.is_valid())
        self.assertEqual(sponsorship.ledger_entry_type, LedgerEntryType.SPONSORSHIP)
        self.assertEqual(sponsorship.owner, _OWNER)
        self.assertEqual(sponsorship.sponsee, _SPONSEE)
        self.assertEqual(sponsorship.fee_amount, "1000000")
        self.assertEqual(sponsorship.max_fee, "1000")
        self.assertEqual(sponsorship.reserve_count, 0)

    def test_valid_sponsorship_with_reserve_count(self):
        """Test creating a valid Sponsorship with reserve_count."""
        sponsorship = Sponsorship(
            owner=_OWNER,
            sponsee=_SPONSEE,
            owner_node=_OWNER_NODE,
            sponsee_node=_SPONSEE_NODE,
            reserve_count=5,
            flags=0,
        )
        self.assertTrue(sponsorship.is_valid())
        self.assertEqual(sponsorship.reserve_count, 5)
        self.assertIsNone(sponsorship.fee_amount)

    def test_valid_sponsorship_with_both_fee_and_reserve(self):
        """Test creating a valid Sponsorship with both fee_amount and reserve_count."""
        sponsorship = Sponsorship(
            owner=_OWNER,
            sponsee=_SPONSEE,
            owner_node=_OWNER_NODE,
            sponsee_node=_SPONSEE_NODE,
            fee_amount="500000",
            max_fee="500",
            reserve_count=3,
            flags=0,
        )
        self.assertTrue(sponsorship.is_valid())
        self.assertEqual(sponsorship.fee_amount, "500000")
        self.assertEqual(sponsorship.reserve_count, 3)

    def test_valid_sponsorship_with_all_fields(self):
        """Test creating a Sponsorship with all optional fields."""
        sponsorship = Sponsorship(
            owner=_OWNER,
            sponsee=_SPONSEE,
            owner_node=_OWNER_NODE,
            sponsee_node=_SPONSEE_NODE,
            fee_amount="1000000",
            max_fee="1000",
            reserve_count=5,
            flags=SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE,
            previous_txn_id=_PREVIOUS_TXN_ID,
            previous_txn_lgr_seq=_PREVIOUS_TXN_LGR_SEQ,
            index=_INDEX,
        )
        self.assertTrue(sponsorship.is_valid())
        self.assertEqual(sponsorship.previous_txn_id, _PREVIOUS_TXN_ID)
        self.assertEqual(sponsorship.previous_txn_lgr_seq, _PREVIOUS_TXN_LGR_SEQ)
        self.assertEqual(sponsorship.index, _INDEX)

    def test_owner_and_sponsee_same_account(self):
        """Test that owner and sponsee cannot be the same account."""
        with self.assertRaises(XRPLModelException) as error:
            Sponsorship(
                owner=_OWNER,
                sponsee=_OWNER,  # Same as owner
                owner_node=_OWNER_NODE,
                sponsee_node=_SPONSEE_NODE,
                fee_amount="1000000",
            )
        self.assertIn(
            "Owner and Sponsee must be different accounts",
            error.exception.args[0],
        )

    def test_missing_both_fee_amount_and_reserve_count(self):
        """Test that at least one of fee_amount or reserve_count must be provided."""
        with self.assertRaises(XRPLModelException) as error:
            Sponsorship(
                owner=_OWNER,
                sponsee=_SPONSEE,
                owner_node=_OWNER_NODE,
                sponsee_node=_SPONSEE_NODE,
                # Missing both fee_amount and reserve_count (reserve_count defaults to 0)
            )
        self.assertIn(
            "At least one of fee_amount or reserve_count must be provided",
            error.exception.args[0],
        )

    def test_negative_fee_amount(self):
        """Test that fee_amount cannot be negative."""
        with self.assertRaises(XRPLModelException) as error:
            Sponsorship(
                owner=_OWNER,
                sponsee=_SPONSEE,
                owner_node=_OWNER_NODE,
                sponsee_node=_SPONSEE_NODE,
                fee_amount="-1000",
            )
        self.assertIn(
            "fee_amount must be non-negative",
            error.exception.args[0],
        )

    def test_negative_reserve_count(self):
        """Test that reserve_count cannot be negative."""
        with self.assertRaises(XRPLModelException) as error:
            Sponsorship(
                owner=_OWNER,
                sponsee=_SPONSEE,
                owner_node=_OWNER_NODE,
                sponsee_node=_SPONSEE_NODE,
                reserve_count=-5,
            )
        self.assertIn(
            "reserve_count must be non-negative",
            error.exception.args[0],
        )

    def test_negative_max_fee(self):
        """Test that max_fee cannot be negative."""
        with self.assertRaises(XRPLModelException) as error:
            Sponsorship(
                owner=_OWNER,
                sponsee=_SPONSEE,
                owner_node=_OWNER_NODE,
                sponsee_node=_SPONSEE_NODE,
                fee_amount="1000000",
                max_fee="-100",
            )
        self.assertIn(
            "max_fee must be non-negative",
            error.exception.args[0],
        )

    def test_invalid_max_fee_format(self):
        """Test that max_fee must be a valid numeric string."""
        with self.assertRaises(XRPLModelException) as error:
            Sponsorship(
                owner=_OWNER,
                sponsee=_SPONSEE,
                owner_node=_OWNER_NODE,
                sponsee_node=_SPONSEE_NODE,
                fee_amount="1000000",
                max_fee="invalid",
            )
        self.assertIn(
            "max_fee must be a valid numeric string",
            error.exception.args[0],
        )


class TestSponsorshipFlag(TestCase):
    """Tests for SponsorshipFlag enum."""

    def test_require_sign_for_fee_flag(self):
        """Test LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE flag value."""
        self.assertEqual(
            SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE,
            0x00010000,
        )
        self.assertEqual(
            SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE.value,
            65536,
        )

    def test_require_sign_for_reserve_flag(self):
        """Test LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE flag value."""
        self.assertEqual(
            SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE,
            0x00020000,
        )
        self.assertEqual(
            SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE.value,
            131072,
        )

    def test_sponsorship_with_require_sign_for_fee_flag(self):
        """Test Sponsorship with LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE flag."""
        sponsorship = Sponsorship(
            owner=_OWNER,
            sponsee=_SPONSEE,
            owner_node=_OWNER_NODE,
            sponsee_node=_SPONSEE_NODE,
            fee_amount="1000000",
            flags=SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE,
        )
        self.assertTrue(sponsorship.is_valid())
        self.assertEqual(
            sponsorship.flags,
            SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE,
        )

    def test_sponsorship_with_require_sign_for_reserve_flag(self):
        """Test Sponsorship with LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE flag."""
        sponsorship = Sponsorship(
            owner=_OWNER,
            sponsee=_SPONSEE,
            owner_node=_OWNER_NODE,
            sponsee_node=_SPONSEE_NODE,
            reserve_count=5,
            flags=SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE,
        )
        self.assertTrue(sponsorship.is_valid())
        self.assertEqual(
            sponsorship.flags,
            SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE,
        )

    def test_sponsorship_with_both_flags(self):
        """Test Sponsorship with both flags combined."""
        combined_flags = (
            SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE
            | SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE
        )
        sponsorship = Sponsorship(
            owner=_OWNER,
            sponsee=_SPONSEE,
            owner_node=_OWNER_NODE,
            sponsee_node=_SPONSEE_NODE,
            fee_amount="1000000",
            reserve_count=5,
            flags=combined_flags,
        )
        self.assertTrue(sponsorship.is_valid())
        self.assertEqual(sponsorship.flags, 0x00030000)
        # Verify both flags are set
        self.assertTrue(
            sponsorship.flags & SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE
        )
        self.assertTrue(
            sponsorship.flags
            & SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE
        )

    def test_enum_members(self):
        """Test that SponsorshipFlag has exactly 2 members."""
        members = list(SponsorshipFlag)
        self.assertEqual(len(members), 2)
        self.assertIn(
            SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_FEE,
            members,
        )
        self.assertIn(
            SponsorshipFlag.LSF_SPONSORSHIP_REQUIRE_SIGN_FOR_RESERVE,
            members,
        )


class TestLedgerEntryType(TestCase):
    """Tests for LedgerEntryType enum."""

    def test_sponsorship_entry_type_exists(self):
        """Test that SPONSORSHIP entry type exists."""
        self.assertTrue(hasattr(LedgerEntryType, "SPONSORSHIP"))
        self.assertEqual(LedgerEntryType.SPONSORSHIP, "Sponsorship")

    def test_sponsorship_entry_type_in_enum(self):
        """Test that SPONSORSHIP is in the enum members."""
        members = list(LedgerEntryType)
        self.assertIn(LedgerEntryType.SPONSORSHIP, members)

    def test_sponsorship_entry_type_string_value(self):
        """Test that SPONSORSHIP has correct string value."""
        self.assertIsInstance(LedgerEntryType.SPONSORSHIP.value, str)
        self.assertEqual(LedgerEntryType.SPONSORSHIP.value, "Sponsorship")

    def test_ledger_entry_type_access_by_name(self):
        """Test accessing SPONSORSHIP by name."""
        self.assertEqual(
            LedgerEntryType["SPONSORSHIP"],
            LedgerEntryType.SPONSORSHIP,
        )

    def test_ledger_entry_type_access_by_value(self):
        """Test accessing SPONSORSHIP by value."""
        self.assertEqual(
            LedgerEntryType("Sponsorship"),
            LedgerEntryType.SPONSORSHIP,
        )

