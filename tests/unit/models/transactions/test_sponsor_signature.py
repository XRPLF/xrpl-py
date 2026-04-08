"""Unit tests for SponsorSignature and SponsorSigner nested models."""

from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.sponsor_signature import (
    SponsorSignature,
    SponsorSigner,
)

_SPONSOR_ACCOUNT = "rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk"
_SIGNER_ACCOUNT_1 = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_SIGNER_ACCOUNT_2 = "rU6K7V3Po4snVhBBaU29sesqs2qTQJWDw1"
_SIGNING_PUB_KEY = "0330E7FC9D56BB25D6893BA3F317AE5BCF33B3291BD63DB32654A313222F7FD020"
_TXN_SIGNATURE = (
    "3045022100CAB9A6F84026D57B05760D5E2395FB7BE86BF39F10DC6E2E69DC91238EE0970B"
    "022058EC36A8EF9EE65F5D0D8CAC4E88C8C19FEF39E40F53D4CCECFE5F68E8E4BF89"
)
_TXN_SIGNATURE_2 = (
    "304402204428BB0896A4D0F3A935C494767C5B0E5A1E2C8F8F8F8F8F8F8F8F8F8F8F8F8F"
    "02201234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF"
)


class TestSponsorSigner(TestCase):
    """Tests for SponsorSigner nested model."""

    def test_valid_sponsor_signer(self):
        """Test creating a valid SponsorSigner."""
        signer = SponsorSigner(
            account=_SIGNER_ACCOUNT_1,
            txn_signature=_TXN_SIGNATURE,
            signing_pub_key=_SIGNING_PUB_KEY,
        )
        self.assertTrue(signer.is_valid())
        self.assertEqual(signer.account, _SIGNER_ACCOUNT_1)
        self.assertEqual(signer.txn_signature, _TXN_SIGNATURE)
        self.assertEqual(signer.signing_pub_key, _SIGNING_PUB_KEY)

    def test_sponsor_signer_missing_required_fields(self):
        """Test that SponsorSigner requires all fields."""
        with self.assertRaises(XRPLModelException):
            SponsorSigner(
                account=_SIGNER_ACCOUNT_1,
                txn_signature=_TXN_SIGNATURE,
                # missing signing_pub_key
            )


class TestSponsorSignature(TestCase):
    """Tests for SponsorSignature nested model."""

    def test_valid_single_signature(self):
        """Test creating a valid single-signed SponsorSignature."""
        sponsor_sig = SponsorSignature(
            signing_pub_key=_SIGNING_PUB_KEY,
            txn_signature=_TXN_SIGNATURE,
        )
        self.assertTrue(sponsor_sig.is_valid())
        self.assertEqual(sponsor_sig.signing_pub_key, _SIGNING_PUB_KEY)
        self.assertEqual(sponsor_sig.txn_signature, _TXN_SIGNATURE)
        self.assertIsNone(sponsor_sig.signers)

    def test_valid_multi_signature(self):
        """Test creating a valid multi-signed SponsorSignature."""
        sponsor_sig = SponsorSignature(
            signing_pub_key="",  # Empty for multi-sig
            signers=[
                SponsorSigner(
                    account=_SIGNER_ACCOUNT_1,
                    txn_signature=_TXN_SIGNATURE,
                    signing_pub_key=_SIGNING_PUB_KEY,
                ),
                SponsorSigner(
                    account=_SIGNER_ACCOUNT_2,
                    txn_signature=_TXN_SIGNATURE_2,
                    signing_pub_key=_SIGNING_PUB_KEY,
                ),
            ],
        )
        self.assertTrue(sponsor_sig.is_valid())
        self.assertEqual(sponsor_sig.signing_pub_key, "")
        self.assertIsNone(sponsor_sig.txn_signature)
        self.assertEqual(len(sponsor_sig.signers), 2)

    def test_missing_both_signature_types(self):
        """Test that either txn_signature or signers must be provided."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY,
                # missing both txn_signature and signers
            )
        self.assertIn(
            "must contain either txn_signature",
            error.exception.args[0],
        )

    def test_both_signature_types_provided(self):
        """Test that both txn_signature and signers cannot be provided."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY,
                txn_signature=_TXN_SIGNATURE,
                signers=[
                    SponsorSigner(
                        account=_SIGNER_ACCOUNT_1,
                        txn_signature=_TXN_SIGNATURE,
                        signing_pub_key=_SIGNING_PUB_KEY,
                    )
                ],
            )
        self.assertIn(
            "cannot contain both txn_signature and signers",
            error.exception.args[0],
        )

    def test_multi_sig_requires_empty_signing_pub_key(self):
        """Test that multi-sig requires empty signing_pub_key."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY,  # Should be empty for multi-sig
                signers=[
                    SponsorSigner(
                        account=_SIGNER_ACCOUNT_1,
                        txn_signature=_TXN_SIGNATURE,
                        signing_pub_key=_SIGNING_PUB_KEY,
                    )
                ],
            )
        self.assertIn(
            "must be empty string for multi-signed sponsors",
            error.exception.args[0],
        )

    def test_single_sig_requires_non_empty_signing_pub_key(self):
        """Test that single-sig requires non-empty signing_pub_key."""
        with self.assertRaises(XRPLModelException) as error:
            SponsorSignature(
                signing_pub_key="",  # Should not be empty for single-sig
                txn_signature=_TXN_SIGNATURE,
            )
        self.assertIn(
            "signing_pub_key is required for single-signed sponsors",
            error.exception.args[0],
        )

    def test_max_signers_limit(self):
        """Test that maximum of 8 signers is enforced."""
        signers = [
            SponsorSigner(
                account=f"rAccount{i}",
                txn_signature=_TXN_SIGNATURE,
                signing_pub_key=_SIGNING_PUB_KEY,
            )
            for i in range(9)  # 9 signers (exceeds limit)
        ]
        with self.assertRaises(XRPLModelException) as error:
            SponsorSignature(
                signing_pub_key="",
                signers=signers,
            )
        self.assertIn(
            "Maximum of 8 signers allowed",
            error.exception.args[0],
        )

