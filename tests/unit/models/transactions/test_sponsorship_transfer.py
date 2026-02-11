from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import SponsorshipTransfer, SponsorSignature

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_SPONSOR = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_OBJECT_ID = "E6DBAFC99223B42257915A63DFC6B0C032D4070F9A574B255AD97466726FC321"
_SIGNING_PUB_KEY = "0330E7FC9D56BB25D6893BA3F317AE5BCF33B3291BD63DB32654A313222F7FD020"
_TXN_SIGNATURE = "3045022100D184EB4AE5956FF600E7536EE459345C7BBCF097A84CC61A93B9AF7197EDB98702201CEA8009B7BEEBAA2AACC0359B41C427C1C5B550A4CA4B80CF2174AF2D6D5DCE"

# Sponsorship flags
TF_SPONSOR_FEE = 0x00000001
TF_SPONSOR_RESERVE = 0x00000002


class TestSponsorshipTransfer(TestCase):
    def test_valid_sponsorship_transfer_with_all_fields(self):
        """Test valid SponsorshipTransfer with all fields."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_SPONSOR,
            sponsor_flags=TF_SPONSOR_RESERVE,
            sponsor_signature=SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY,
                txn_signature=_TXN_SIGNATURE,
            ),
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.object_id, _OBJECT_ID)
        self.assertEqual(tx.sponsor, _SPONSOR)
        self.assertEqual(tx.sponsor_flags, TF_SPONSOR_RESERVE)

    def test_valid_sponsorship_transfer_with_object_id(self):
        """Test valid SponsorshipTransfer for a specific object."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_SPONSOR,
            sponsor_flags=TF_SPONSOR_RESERVE,
            sponsor_signature=SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY,
                txn_signature=_TXN_SIGNATURE,
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_valid_sponsorship_transfer_without_object_id(self):
        """Test valid SponsorshipTransfer for account (no object_id)."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsor=_SPONSOR,
            sponsor_flags=TF_SPONSOR_RESERVE,
            sponsor_signature=SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY,
                txn_signature=_TXN_SIGNATURE,
            ),
        )
        self.assertTrue(tx.is_valid())
        self.assertIsNone(tx.object_id)

    def test_sponsor_without_sponsor_flags(self):
        """Test error when Sponsor is present but SponsorFlags is missing."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor=_SPONSOR,
                sponsor_signature=SponsorSignature(
                    signing_pub_key=_SIGNING_PUB_KEY,
                    txn_signature=_TXN_SIGNATURE,
                ),
            )
        self.assertIn("sponsor_flags", str(error.exception))

    def test_sponsor_without_sponsor_signature(self):
        """Test error when Sponsor is present but SponsorSignature is missing."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor=_SPONSOR,
                sponsor_flags=TF_SPONSOR_RESERVE,
            )
        self.assertIn("sponsor_signature", str(error.exception))

    def test_sponsor_flags_without_sponsor(self):
        """Test error when SponsorFlags is present but Sponsor is missing."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor_flags=TF_SPONSOR_RESERVE,
            )
        self.assertIn("sponsor", str(error.exception))

    def test_sponsor_signature_without_sponsor(self):
        """Test error when SponsorSignature is present but Sponsor is missing."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor_signature=SponsorSignature(
                    signing_pub_key=_SIGNING_PUB_KEY,
                    txn_signature=_TXN_SIGNATURE,
                ),
            )
        self.assertIn("sponsor_for_signature", str(error.exception))

    def test_invalid_sponsor_flags(self):
        """Test error for invalid SponsorFlags values."""
        invalid_flag = 0x00000004  # Invalid flag
        with self.assertRaises(XRPLModelException) as error:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor=_SPONSOR,
                sponsor_flags=invalid_flag,
                sponsor_signature=SponsorSignature(
                    signing_pub_key=_SIGNING_PUB_KEY,
                    txn_signature=_TXN_SIGNATURE,
                ),
            )
        self.assertIn("sponsor_flags_invalid", str(error.exception))

    def test_valid_sponsor_flags_fee(self):
        """Test valid SponsorshipTransfer with tfSponsorFee flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsor=_SPONSOR,
            sponsor_flags=TF_SPONSOR_FEE,
            sponsor_signature=SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY,
                txn_signature=_TXN_SIGNATURE,
            ),
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.sponsor_flags, TF_SPONSOR_FEE)

    def test_valid_sponsor_flags_reserve(self):
        """Test valid SponsorshipTransfer with tfSponsorReserve flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsor=_SPONSOR,
            sponsor_flags=TF_SPONSOR_RESERVE,
            sponsor_signature=SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY,
                txn_signature=_TXN_SIGNATURE,
            ),
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.sponsor_flags, TF_SPONSOR_RESERVE)

    def test_valid_sponsor_flags_both(self):
        """Test valid SponsorshipTransfer with both flags."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsor=_SPONSOR,
            sponsor_flags=TF_SPONSOR_FEE | TF_SPONSOR_RESERVE,
            sponsor_signature=SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY,
                txn_signature=_TXN_SIGNATURE,
            ),
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.sponsor_flags, TF_SPONSOR_FEE | TF_SPONSOR_RESERVE)

    def test_sponsorship_transfer_minimal(self):
        """Test minimal SponsorshipTransfer (no sponsor, transferring back to sponsee)."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
        )
        self.assertTrue(tx.is_valid())
        self.assertIsNone(tx.sponsor)
        self.assertIsNone(tx.sponsor_flags)
        self.assertIsNone(tx.sponsor_signature)

