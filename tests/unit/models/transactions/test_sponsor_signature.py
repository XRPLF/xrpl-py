from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.transaction import Signer

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_ACCOUNT2 = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"
_SIGNING_PUB_KEY = "ED5F5AC43F527AE97194AC44903F8E0397F1B8AFDC25990B3B8F093E2D1D8B0E2D"
_TXN_SIGNATURE = (
    "304402203B9B0B6E0735AD5F370B2B0B3A81CDE62CC5B7C3"
    "3C5B15C76C3E4B8A0CEEF10220523D4C16C3F68C0840F1B1"
    "F4BF7D5F1C6D3DA2F9D0E4EB7A4E6BF1C3A5D7E9"
)

# CK TODO: Update the tests to ensure that empty SponsorSignature objects fail with an appropriate error


class TestSponsorSignature(TestCase):
    def test_valid_empty(self):
        """SponsorSignature with no fields (all optional)."""
        sig = SponsorSignature()
        self.assertTrue(sig.is_valid())

    def test_valid_with_signing_pub_key(self):
        """Single signature with signing_pub_key."""
        sig = SponsorSignature(
            signing_pub_key=_SIGNING_PUB_KEY,
        )
        self.assertTrue(sig.is_valid())

    def test_valid_with_txn_signature(self):
        """With txn_signature."""
        sig = SponsorSignature(
            txn_signature=_TXN_SIGNATURE,
        )
        self.assertTrue(sig.is_valid())

    def test_valid_with_single_signature(self):
        """Both signing_pub_key and txn_signature."""
        sig = SponsorSignature(
            signing_pub_key=_SIGNING_PUB_KEY,
            txn_signature=_TXN_SIGNATURE,
        )
        self.assertTrue(sig.is_valid())

    def test_valid_with_signers(self):
        """Multi-signature with signers list."""
        sig = SponsorSignature(
            signers=[
                Signer(
                    account=_ACCOUNT,
                    signing_pub_key=_SIGNING_PUB_KEY,
                    txn_signature=_TXN_SIGNATURE,
                ),
                Signer(
                    account=_ACCOUNT2,
                    signing_pub_key=_SIGNING_PUB_KEY,
                    txn_signature=_TXN_SIGNATURE,
                ),
            ],
        )
        self.assertTrue(sig.is_valid())

    def test_to_dict(self):
        """Verify serialization to dict works correctly."""
        sig = SponsorSignature(
            signing_pub_key=_SIGNING_PUB_KEY,
            txn_signature=_TXN_SIGNATURE,
        )
        result = sig.to_dict()
        self.assertEqual(result["signing_pub_key"], _SIGNING_PUB_KEY)
        self.assertEqual(result["txn_signature"], _TXN_SIGNATURE)

    def test_from_dict(self):
        """Verify deserialization from dict works correctly."""
        data = {
            "signing_pub_key": _SIGNING_PUB_KEY,
            "txn_signature": _TXN_SIGNATURE,
        }
        sig = SponsorSignature.from_dict(data)
        self.assertEqual(sig.signing_pub_key, _SIGNING_PUB_KEY)
        self.assertEqual(sig.txn_signature, _TXN_SIGNATURE)
        self.assertTrue(sig.is_valid())

    def test_to_dict_empty(self):
        """Verify empty SponsorSignature serializes correctly."""
        sig = SponsorSignature()
        result = sig.to_dict()
        self.assertIsInstance(result, dict)

    def test_from_dict_empty(self):
        """Verify empty dict deserializes correctly."""
        sig = SponsorSignature.from_dict({})
        self.assertTrue(sig.is_valid())
