"""Tests for sponsor common fields on Transaction base class."""

from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.batch import Batch
from xrpl.models.transactions.payment import Payment
from xrpl.models.transactions.pseudo_transactions import EnableAmendment
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.transaction import Signer

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_SPONSOR = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"
_DESTINATION = "rN7n7otQDd6FczFgLdlqtyMVrn3HMfXpf"


class TestSponsorCommonFields(TestCase):
    def test_payment_with_sponsor_fee(self):
        """Payment with sponsor and tfSponsorFee flag."""
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
            sponsor=_SPONSOR,
            sponsor_flags=0x00000001,  # tfSponsorFee
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(d["sponsor"], _SPONSOR)
        self.assertEqual(d["sponsor_flags"], 1)

    def test_payment_with_sponsor_reserve(self):
        """Payment with sponsor and tfSponsorReserve flag."""
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
            sponsor=_SPONSOR,
            sponsor_flags=0x00000002,  # tfSponsorReserve
        )
        self.assertTrue(tx.is_valid())

    def test_payment_with_sponsor_both_flags(self):
        """Payment with sponsor covering both fee and reserve."""
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
            sponsor=_SPONSOR,
            sponsor_flags=0x00000003,  # tfSponsorFee | tfSponsorReserve
        )
        self.assertTrue(tx.is_valid())

    def test_payment_with_sponsor_signature(self):
        """Payment with full sponsor co-signing."""
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
            sponsor=_SPONSOR,
            sponsor_flags=0x00000001,
            sponsor_signature=SponsorSignature(
                signing_pub_key="ED000000",
                txn_signature="DEADBEEF",
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_payment_with_sponsor_multisig(self):
        """Payment with sponsor multi-signature."""
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
            sponsor=_SPONSOR,
            sponsor_flags=0x00000001,
            sponsor_signature=SponsorSignature(
                signers=[
                    Signer(
                        account=_SPONSOR,
                        signing_pub_key="ED000000",
                        txn_signature="DEADBEEF",
                    )
                ]
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_payment_without_sponsor(self):
        """Regular payment without any sponsor fields."""
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertNotIn("sponsor", d)
        self.assertNotIn("sponsor_flags", d)
        self.assertNotIn("sponsor_signature", d)

    # ── XLS-68 §8.3.4: transactions that cannot be sponsored ──

    _UNSPONSORABLE_MSG = "cannot be sponsored"

    def _batch(self, **kwargs):
        inner_tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
        )
        return Batch(
            account=_ACCOUNT,
            raw_transactions=[inner_tx, inner_tx],
            **kwargs,
        )

    def test_batch_with_sponsor_fee_allowed(self):
        """An outer Batch may be fee-sponsored (spfSponsorFee).

        Per XLS-68 §13.2, only reserve sponsorship is disallowed on the outer
        Batch; fee sponsorship follows the standard rules. rippled only rejects
        `isReserveSponsored` on the outer Batch (Batch.cpp preflight).
        """
        tx = self._batch(sponsor=_SPONSOR, sponsor_flags=1)
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.sponsor, _SPONSOR)
        self.assertEqual(tx.sponsor_flags, 1)

    def test_batch_with_sponsor_reserve_rejected(self):
        """An outer Batch must not use spfSponsorReserve (XLS-68 §13.4.1)."""
        with self.assertRaises(XRPLModelException) as cm:
            self._batch(sponsor=_SPONSOR, sponsor_flags=2)
        self.assertIn("not allowed on an outer Batch", str(cm.exception))

    def test_batch_with_sponsor_fee_and_reserve_rejected(self):
        """spfSponsorReserve is rejected on an outer Batch even alongside fee."""
        with self.assertRaises(XRPLModelException) as cm:
            self._batch(sponsor=_SPONSOR, sponsor_flags=3)
        self.assertIn("not allowed on an outer Batch", str(cm.exception))

    def test_pseudo_transaction_with_sponsor_rejected(self):
        """Pseudo-transaction with sponsor is rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            EnableAmendment(
                amendment="A" * 64,
                ledger_sequence=1,
                sponsor=_SPONSOR,
                sponsor_flags=1,
            )
        self.assertIn(self._UNSPONSORABLE_MSG, str(cm.exception))
