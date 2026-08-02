"""Unit tests for sign_as_sponsor (XLS-0068)."""

from unittest import TestCase

from xrpl.constants import XRPLException
from xrpl.core.binarycodec import encode_for_multisigning, encode_for_signing
from xrpl.core.keypairs import is_valid_message
from xrpl.models.transactions import Payment
from xrpl.transaction import multisign, sign, sign_as_sponsor
from xrpl.wallet import Wallet

SPONSEE = Wallet.create()
SPONSOR = Wallet.create()
DESTINATION = Wallet.create()
SPONSEE_KEY_A = Wallet.create()
SPONSEE_KEY_B = Wallet.create()


def _payment(**kwargs) -> Payment:
    return Payment(
        account=SPONSEE.address,
        destination=DESTINATION.address,
        amount="1000",
        sequence=1,
        fee="40",
        last_ledger_sequence=100,
        sponsor=SPONSOR.address,
        sponsor_flags=1,  # spfSponsorFee
        **kwargs,
    )


def _sponsee_multisigned() -> Payment:
    """A sponsee-multisigned transaction: SigningPubKey stays empty."""
    tx = _payment()
    return multisign(
        tx,
        [
            sign(tx, SPONSEE_KEY_A, multisign=True),
            sign(tx, SPONSEE_KEY_B, multisign=True),
        ],
    )


def _verify(tx, signature: str, public_key: str) -> bool:
    return is_valid_message(
        bytes.fromhex(encode_for_signing(tx.to_xrpl())),
        bytes.fromhex(signature),
        public_key,
    )


class TestSignAsSponsor(TestCase):
    """The sponsor's signature covers the transaction's signing fields.

    ``SponsorSignature`` is not itself a signing field, and neither is the
    sponsee's ``TxnSignature``, so the two parties' signatures are independent
    and may be produced in either order. Only ``SigningPubKey`` -- which *is* a
    signing field -- must be settled before the sponsor signs.
    """

    def test_spec_order_sponsee_sets_pubkey_then_sponsor_signs(self):
        """The sponsee need not have signed, only set its key."""
        tx = _payment(signing_pub_key=SPONSEE.public_key)
        self.assertFalse(tx.is_signed())

        result = sign_as_sponsor(SPONSOR, tx)
        sponsor_sig = result.tx.sponsor_signature

        # The signature is the sponsor's, not the sponsee's.
        self.assertFalse(_verify(tx, sponsor_sig.txn_signature, SPONSEE.public_key))
        self.assertTrue(
            _verify(tx, sponsor_sig.txn_signature, sponsor_sig.signing_pub_key)
        )

        # The sponsee signs last; that adds only TxnSignature, which is not a
        # signing field, so the sponsor's signature survives.
        final = sign(result.tx, SPONSEE)
        self.assertTrue(
            _verify(final, final.sponsor_signature.txn_signature, SPONSOR.public_key)
        )
        self.assertTrue(_verify(final, final.txn_signature, final.signing_pub_key))

    def test_reverse_order_sponsee_signs_first(self):
        """Signing order is interchangeable; both signatures stay valid."""
        signed = sign(_payment(), SPONSEE)
        final = sign_as_sponsor(SPONSOR, signed).tx

        self.assertTrue(
            _verify(final, final.sponsor_signature.txn_signature, SPONSOR.public_key)
        )
        self.assertTrue(_verify(final, final.txn_signature, final.signing_pub_key))

    def test_empty_signing_pub_key_rejected_by_default(self):
        """An unset SigningPubKey would invalidate the sponsor's signature."""
        with self.assertRaises(XRPLException) as ctx:
            sign_as_sponsor(SPONSOR, _payment())
        self.assertIn("sponsee_multisign", str(ctx.exception))

    def test_sponsee_multisign_allows_empty_signing_pub_key(self):
        """An empty SigningPubKey is the ledger's marker for multi-signing.

        The sponsee's keys live in ``Signers``; ``SigningPubKey`` stays empty
        permanently, so it cannot change and invalidate the sponsor's signature.
        """
        tx = _sponsee_multisigned()
        self.assertEqual(tx.signing_pub_key, "")
        self.assertEqual(len(tx.signers), 2)
        self.assertTrue(tx.is_signed())

        result = sign_as_sponsor(SPONSOR, tx, sponsee_multisign=True)
        sponsor_sig = result.tx.sponsor_signature

        self.assertTrue(
            _verify(result.tx, sponsor_sig.txn_signature, sponsor_sig.signing_pub_key)
        )
        # The sponsee's own signatures are untouched.
        self.assertEqual(len(result.tx.signers), 2)
        self.assertTrue(result.tx.is_signed())

    def test_sponsee_multisign_payload_is_stable(self):
        """The sponsor may sign before or after a multi-signing sponsee."""
        before = _payment()
        after = _sponsee_multisigned()
        self.assertEqual(
            encode_for_signing(before.to_xrpl()),
            encode_for_signing(after.to_xrpl()),
        )

    def test_both_parties_multisign(self):
        """`multisign` and `sponsee_multisign` are independent."""
        tx = _sponsee_multisigned()
        sponsor_keys = [Wallet.create(), Wallet.create()]
        parts = [
            sign_as_sponsor(key, tx, multisign=True, sponsee_multisign=True)
            for key in sponsor_keys
        ]
        for key, part in zip(sponsor_keys, parts):
            signer = part.tx.sponsor_signature.signers[0]
            self.assertEqual(signer.account, key.address)
            self.assertTrue(
                is_valid_message(
                    bytes.fromhex(encode_for_multisigning(tx.to_xrpl(), key.address)),
                    bytes.fromhex(signer.txn_signature),
                    signer.signing_pub_key,
                )
            )

    def test_sponsee_multisign_does_not_bypass_other_guards(self):
        """The flag only relaxes the SigningPubKey check."""
        no_sponsor = Payment(
            account=SPONSEE.address,
            destination=DESTINATION.address,
            amount="1000",
            sequence=1,
            fee="40",
        )
        with self.assertRaises(XRPLException):
            sign_as_sponsor(SPONSOR, no_sponsor, sponsee_multisign=True)

        no_fee = Payment(
            account=SPONSEE.address,
            destination=DESTINATION.address,
            amount="1000",
            sequence=1,
            sponsor=SPONSOR.address,
            sponsor_flags=1,
        )
        with self.assertRaises(XRPLException):
            sign_as_sponsor(SPONSOR, no_fee, sponsee_multisign=True)
