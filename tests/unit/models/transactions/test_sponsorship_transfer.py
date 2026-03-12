from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.sponsorship_transfer import (
    SponsorshipTransfer,
    SponsorshipTransferFlag,
)
from xrpl.models.transactions.types import TransactionType

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_ACCOUNT2 = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"
_OBJECT_ID = "DB303FC1C7611B22C09E773B51044F6BEA02EF917DF59A2E2860871E167066A5"


class TestSponsorshipTransfer(TestCase):
    def test_valid_minimal(self):
        """SponsorshipTransfer with just account."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_object_id(self):
        """Setting object_id (hex string, 64 chars)."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_sponsee(self):
        """Setting sponsee."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_all_fields(self):
        """Both object_id and sponsee set."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_end_flag(self):
        """Using TF_SPONSORSHIP_END flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_create_flag(self):
        """Using TF_SPONSORSHIP_CREATE flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_reassign_flag(self):
        """Using TF_SPONSORSHIP_REASSIGN flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
        )
        self.assertTrue(tx.is_valid())

    def test_has_correct_transaction_type(self):
        """Verify transaction_type is TransactionType.SPONSORSHIP_TRANSFER."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
        )
        self.assertEqual(tx.transaction_type, TransactionType.SPONSORSHIP_TRANSFER)

    def test_valid_with_flags_and_all_fields(self):
        """All fields plus a flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertTrue(tx.is_valid())
