"""
Combined Unit Tests for XLS-0068 Sponsored Fees and Reserves Implementation

This file combines all unit tests from the XLS-0068 implementation into a single
test file for convenience. It includes tests for:
- Phase 1: Core Data Models (SponsorSignature, SponsorshipType, GranularPermission)
- Phase 2: Ledger Entry Types (Sponsorship, SponsorshipFlag, LedgerEntryType)
- Phase 3: Transaction Types (SponsorshipSet, SponsorshipTransfer)
- Phase 4: Transaction Base Class Updates (sponsor, sponsor_flags, sponsor_signature)
- Phase 5: RPC Methods (AccountSponsoring)

Total: 91 unit tests

Run with: python3 -m unittest test_xls0068_combined -v
"""

from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.ledger_objects import LedgerEntryType, Sponsorship, SponsorshipFlag
from xrpl.models.requests import AccountSponsoring
from xrpl.models.transactions import (
    DelegateSet,
    Payment,
    SponsorshipSet,
    SponsorshipTransfer,
)
from xrpl.models.transactions.delegate_set import GranularPermission, Permission
from xrpl.models.transactions.sponsor_signature import (
    SponsorSignature,
    SponsorSigner,
)
from xrpl.models.transactions.sponsorship_set import (
    SponsorshipSetFlag,
    SponsorshipSetFlagInterface,
)
from xrpl.models.transactions.types import SponsorshipType

# Test constants
_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_SPONSOR_ACCOUNT = "rN7n7otQDd6FczFgLdlqtyMVrn3HMfXoKk"
_SIGNER_ACCOUNT_1 = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_SIGNER_ACCOUNT_2 = "rU6K7V3Po4snVhBBaU29sesqs2qTQJWDw1"
_SPONSEE = "rfkDkFai4jUfCvAJiZ5Vm7XvvWjYvDqeYo"
_DELEGATED_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_SIGNING_PUB_KEY = "0330E7FC9D56BB25D6893BA3F317AE5BCF33B3291BD63DB32654A313222F7FD020"
_TXN_SIGNATURE = (
    "3045022100CAB9A6F84026D57B05760D5E2395FB7BE86BF39F10DC6E2E69DC91238EE0970B"
    "022058EC36A8EF9EE65F5D0D8CAC4E88C8C19FEF39E40F53D4CCECFE5F68E8E4BF89"
)
_TXN_SIGNATURE_2 = (
    "304402204428BB0896A4D0F3A935C494767C5B0E5A1E2C8F8F8F8F8F8F8F8F8F8F8F8F8F"
    "02201234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF"
)
_OBJECT_ID = "E6DBAFC99223B42257915A63DFC6B0C032D4070F9A574B255AD97466726FC321"
_OWNER_NODE = "0000000000000000"
_SPONSEE_NODE = "0000000000000000"
_PREVIOUS_TXN_ID = "1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF"
_PREVIOUS_TXN_LGR_SEQ = 12345678
_INDEX = "ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789"

# Sponsorship flags
TF_SPONSOR_FEE = 0x00000001
TF_SPONSOR_RESERVE = 0x00000002


# =============================================================================
# PHASE 1: CORE DATA MODELS
# =============================================================================


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

