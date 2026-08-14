from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import SponsorshipSet
from xrpl.models.transactions.sponsorship_set import (
    SponsorshipSetFlag,
    SponsorshipSetFlagInterface,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_SPONSEE = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_SPONSOR = "rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk"


class TestSponsorshipSet(TestCase):
    def test_valid_sponsorship_set_with_sponsee(self):
        """Test valid SponsorshipSet where Account is the sponsor."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_SPONSEE,
            fee_amount="1000000",
            max_fee="100",
            reserve_count=5,
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.account, _ACCOUNT)
        self.assertEqual(tx.sponsee, _SPONSEE)

    def test_valid_sponsorship_set_with_sponsor_and_delete(self):
        """Test valid SponsorshipSet where Account is the sponsee deleting."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsor=_SPONSOR,
            flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.account, _ACCOUNT)
        self.assertEqual(tx.sponsor, _SPONSOR)

    def test_both_sponsor_and_sponsee_specified(self):
        """Test error when both Sponsor and Sponsee are specified."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsor=_SPONSOR,
                sponsee=_SPONSEE,
                fee_amount="1000000",
            )
        self.assertIn("sponsor_sponsee", str(error.exception))

    def test_neither_sponsor_nor_sponsee_specified(self):
        """Test error when neither Sponsor nor Sponsee is specified."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                fee_amount="1000000",
            )
        self.assertIn("sponsor_sponsee", str(error.exception))

    def test_account_same_as_sponsee(self):
        """Test error when Account is the same as Sponsee."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT,
                fee_amount="1000000",
            )
        self.assertIn("account", str(error.exception))

    def test_self_sponsorship(self):
        """Test error for self-sponsorship."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsor=_ACCOUNT,
                flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
            )
        self.assertIn("self_sponsorship", str(error.exception))

    def test_sponsor_field_without_delete_flag(self):
        """Test error when Sponsor field is present without tfDeleteObject."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsor=_SPONSOR,
                fee_amount="1000000",
            )
        self.assertIn("sponsor_field", str(error.exception))

    def test_delete_flag_with_fee_amount(self):
        """Test error when tfDeleteObject is used with FeeAmount."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsor=_SPONSOR,
                flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
                fee_amount="1000000",
            )
        self.assertIn("fee_amount_with_delete", str(error.exception))

    def test_delete_flag_with_max_fee(self):
        """Test error when tfDeleteObject is used with MaxFee."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsor=_SPONSOR,
                flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
                max_fee="100",
            )
        self.assertIn("max_fee_with_delete", str(error.exception))

    def test_delete_flag_with_reserve_count(self):
        """Test error when tfDeleteObject is used with ReserveCount."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsor=_SPONSOR,
                flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
                reserve_count=5,
            )
        self.assertIn("reserve_count_with_delete", str(error.exception))

    def test_delete_flag_with_signature_requirement_flag(self):
        """Test error when tfDeleteObject is used with signature requirement flags."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsor=_SPONSOR,
                flags=(
                    SponsorshipSetFlag.TF_DELETE_OBJECT
                    | SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE
                ),
            )
        self.assertIn("invalid_flag_with_delete", str(error.exception))

    def test_negative_max_fee(self):
        """Test error for negative MaxFee."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_SPONSEE,
                fee_amount="1000000",
                max_fee="-100",
            )
        self.assertIn("max_fee", str(error.exception))

    def test_invalid_max_fee_format(self):
        """Test error for invalid MaxFee format."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_SPONSEE,
                fee_amount="1000000",
                max_fee="invalid",
            )
        self.assertIn("max_fee", str(error.exception))

