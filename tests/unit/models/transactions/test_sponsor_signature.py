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


class TestSponsorSignature(TestCase):
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

    def test_valid_sponsor_signature_single_sig(self):
        """SponsorSignature with both signing_pub_key and txn_signature is valid."""
        sig = SponsorSignature(
            signing_pub_key="ED000000",
            txn_signature="DEADBEEF",
        )
        self.assertTrue(sig.is_valid())

    def test_valid_sponsor_signature_multi_sig(self):
        """SponsorSignature with signers list is valid."""
        sig = SponsorSignature(
            signers=[
                Signer(
                    account=_ACCOUNT2,
                    signing_pub_key="ED000000",
                    txn_signature="DEADBEEF",
                )
            ]
        )
        self.assertTrue(sig.is_valid())

    def test_invalid_sponsor_signature_empty(self):
        """SponsorSignature with no fields set must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorSignature()
        self.assertIn(
            "Must provide either (`signing_pub_key` + `txn_signature`) "
            "for single-signature or `signers` for multi-signature.",
            str(cm.exception),
        )

    def test_invalid_sponsor_signature_missing_txn_signature(self):
        """signing_pub_key without txn_signature must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorSignature(signing_pub_key="ED000000")
        self.assertIn(
            "`txn_signature` is required when `signing_pub_key` is set.",
            str(cm.exception),
        )

    def test_invalid_sponsor_signature_missing_pub_key(self):
        """txn_signature without signing_pub_key must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorSignature(txn_signature="DEADBEEF")
        self.assertIn(
            "`signing_pub_key` is required when `txn_signature` is set.",
            str(cm.exception),
        )

    def test_invalid_sponsor_signature_single_and_multi(self):
        """Providing both single-sig fields and signers must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorSignature(
                signing_pub_key="ED000000",
                txn_signature="DEADBEEF",
                signers=[
                    Signer(
                        account=_ACCOUNT2,
                        signing_pub_key="ED000000",
                        txn_signature="DEADBEEF",
                    )
                ],
            )
        self.assertIn(
            "Cannot set both single-signature fields "
            "(`signing_pub_key`/`txn_signature`) and `signers`.",
            str(cm.exception),
        )
