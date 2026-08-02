from unittest import TestCase

from xrpl.core.binarycodec import decode, encode, encode_for_signing
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.payment import Payment
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.transaction import Signer, TransactionFlag

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_ACCOUNT2 = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"

# `_ACCOUNT2` above does not pass address-checksum validation, which the model
# layer never applies but the binary codec does. These two are checksum-valid
# and so are usable in tests that actually encode a transaction.
_DESTINATION = "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"
_SPONSOR = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
_SIGNING_PUB_KEY = "ED5F5AC43F527AE97194AC44903F8E0397F1B8AFDC25990B3B8F093E2D1D8B0E2D"
_TXN_SIGNATURE = (
    "304402203B9B0B6E0735AD5F370B2B0B3A81CDE62CC5B7C3"
    "3C5B15C76C3E4B8A0CEEF10220523D4C16C3F68C0840F1B1"
    "F4BF7D5F1C6D3DA2F9D0E4EB7A4E6BF1C3A5D7E9"
)


def _sponsored_payment(**overrides):
    """A checksum-valid, reserve-sponsored Payment ready to encode."""
    fields = {
        "account": _ACCOUNT,
        "destination": _DESTINATION,
        "amount": "1000000",
        "sequence": 1,
        "fee": "10",
        "signing_pub_key": _SIGNING_PUB_KEY,
        "sponsor": _SPONSOR,
        "sponsor_flags": 2,
    }
    fields.update(overrides)
    return Payment(**fields)


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

    def test_valid_empty_placeholder(self):
        """An empty SponsorSignature is valid -- it is a required placeholder.

        A Batch inner transaction naming a `sponsor` must carry an
        empty `SponsorSignature`; its presence (not its contents) is what tells
        the ledger the sponsor needs a `BatchSigners` entry. `simulate`
        autofills the sponsor signing fields only when the field is present.
        rippled has no preflight rule requiring it to be non-empty.
        """
        sig = SponsorSignature()
        self.assertTrue(sig.is_valid())
        self.assertIsNone(sig.signing_pub_key)
        self.assertIsNone(sig.txn_signature)
        self.assertIsNone(sig.signers)

    def test_empty_placeholder_serializes_to_empty_object(self):
        """The empty placeholder must reach the wire as an empty STObject."""
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
            sequence=0,
            fee="0",
            signing_pub_key="",
            flags=TransactionFlag.TF_INNER_BATCH_TXN,
            sponsor=_SPONSOR,
            sponsor_flags=2,
            sponsor_signature=SponsorSignature(),
        )
        self.assertEqual(tx.to_xrpl()["SponsorSignature"], {})

        # Survives a full binary round trip and rehydrates as the model type.
        decoded = decode(encode(tx.to_xrpl()))
        self.assertEqual(decoded["SponsorSignature"], {})
        self.assertEqual(
            Payment.from_xrpl(decoded).sponsor_signature, SponsorSignature()
        )

    def test_populated_sponsor_signature_round_trips(self):
        """Both the single-signed and multi-signed shapes survive the wire.

        The empty placeholder is covered above; these are the shapes that
        actually carry signatures, and only ``is_valid()`` had exercised them.
        """
        single = SponsorSignature(
            signing_pub_key=_SIGNING_PUB_KEY, txn_signature=_TXN_SIGNATURE
        )
        multi = SponsorSignature(
            signers=[
                Signer(
                    account=_SPONSOR,
                    signing_pub_key=_SIGNING_PUB_KEY,
                    txn_signature=_TXN_SIGNATURE,
                )
            ]
        )
        for label, sponsor_signature in (("single", single), ("multi", multi)):
            with self.subTest(shape=label):
                tx = _sponsored_payment(sponsor_signature=sponsor_signature)
                rehydrated = Payment.from_xrpl(decode(encode(tx.to_xrpl())))
                self.assertEqual(rehydrated.sponsor_signature, sponsor_signature)

    def test_sponsor_signature_is_absent_from_the_signing_payload(self):
        """``sfSponsorSignature`` is kNotSigning, so it cannot sign over itself.

        This is what lets the sponsor sign a transaction the sponsee has already
        signed: attaching the sponsor's signature leaves the payload both parties
        signed byte-identical. If the field were a signing field, the sponsor's
        own signature would invalidate the sponsee's.
        """
        unsigned = _sponsored_payment()
        signed = _sponsored_payment(
            sponsor_signature=SponsorSignature(
                signing_pub_key=_SIGNING_PUB_KEY, txn_signature=_TXN_SIGNATURE
            )
        )
        self.assertEqual(
            encode_for_signing(unsigned.to_xrpl()),
            encode_for_signing(signed.to_xrpl()),
        )
        # It is still serialized -- just not signed over.
        self.assertIn("SponsorSignature", decode(encode(signed.to_xrpl())))

    def test_sponsor_and_sponsor_flags_are_in_the_signing_payload(self):
        """The terms of the sponsorship are signed, so they are tamper-evident.

        The signature does not cover ``SponsorSignature``, but it must cover who
        the sponsor is and what they agreed to pay for -- otherwise either party
        could rewrite the deal after the other signed.
        """
        baseline = encode_for_signing(_sponsored_payment().to_xrpl())
        self.assertNotEqual(
            baseline,
            encode_for_signing(_sponsored_payment(sponsor=_DESTINATION).to_xrpl()),
        )
        self.assertNotEqual(
            baseline,
            encode_for_signing(_sponsored_payment(sponsor_flags=1).to_xrpl()),
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
