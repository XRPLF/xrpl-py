"""Tests for sponsor common fields on Transaction base class."""

from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.batch import Batch
from xrpl.models.transactions.payment import Payment
from xrpl.models.transactions.pseudo_transactions import EnableAmendment
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.transaction import Signer, SponsorFlag

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

    # ── Transactions that cannot be sponsored ──

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

        Only reserve sponsorship is disallowed on the outer
        Batch; fee sponsorship follows the standard rules. rippled only rejects
        `isReserveSponsored` on the outer Batch (Batch.cpp preflight).
        """
        tx = self._batch(sponsor=_SPONSOR, sponsor_flags=1)
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.sponsor, _SPONSOR)
        self.assertEqual(tx.sponsor_flags, 1)

    def test_batch_with_sponsor_reserve_rejected(self):
        """An outer Batch must not use spfSponsorReserve."""
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


class TestSponsorCommonFieldValidation(TestCase):
    """`sponsor` / `sponsor_flags` are all-or-nothing and must name something."""

    def test_sponsor_requires_sponsor_flags(self):
        """rippled: `hasSponsor != hasSponsorFlags` -> temINVALID_FLAG."""
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT, destination=_DESTINATION, amount="1", sponsor=_SPONSOR
            )
        self.assertIn("`sponsor_flags` is required", str(cm.exception))

    def test_sponsor_flags_may_not_be_zero(self):
        """Zero flags sponsors nothing (rippled: temINVALID_FLAG)."""
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount="1",
                sponsor=_SPONSOR,
                sponsor_flags=0,
            )
        self.assertIn("must not be zero", str(cm.exception))

    def test_delegate_cannot_be_combined_with_reserve_sponsorship(self):
        """The created object's owner would be ambiguous (rippled: temINVALID)."""
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount="1",
                delegate=_SPONSOR,
                sponsor=_DESTINATION,
                sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            )
        self.assertIn("cannot be combined with `spfSponsorReserve`", str(cm.exception))

    def test_delegate_with_fee_sponsorship_is_allowed(self):
        """Only *reserve* sponsorship conflicts with delegation."""
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1",
            delegate=_SPONSOR,
            sponsor=_DESTINATION,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_FEE,
        )
        self.assertTrue(tx.is_valid())

    def test_sponsor_flag_enum_matches_the_wire_values(self):
        """The enum is the documented spelling of the two bits."""
        self.assertEqual(int(SponsorFlag.SPF_SPONSOR_FEE), 0x00000001)
        self.assertEqual(int(SponsorFlag.SPF_SPONSOR_RESERVE), 0x00000002)
        combined = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1",
            sponsor=_SPONSOR,
            sponsor_flags=(
                SponsorFlag.SPF_SPONSOR_FEE | SponsorFlag.SPF_SPONSOR_RESERVE
            ),
        )
        self.assertEqual(combined.to_xrpl()["SponsorFlags"], 3)


class TestBatchInnerSponsorRules(TestCase):
    """An inner transaction is unsigned and its fee is zero.

    Both facts constrain what sponsorship an inner may declare.
    """

    _OTHER = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"

    def _inner(self, **overrides):
        fields = {
            "account": _ACCOUNT,
            "destination": _DESTINATION,
            "amount": "1",
            "fee": "0",
            "sequence": 1,
            "signing_pub_key": "",
            "flags": 0x40000000,
        }
        fields.update(overrides)
        return Payment(**fields)

    def _batch(self, inner):
        return Batch(
            account=_SPONSOR,
            raw_transactions=[inner, self._inner(account=self._OTHER)],
            flags=0x00010000,
            fee="20",
            sequence=1,
        )

    def test_inner_may_not_sponsor_the_fee(self):
        """The outer Batch pays every inner's fee (rippled: temINVALID_FLAG)."""
        with self.assertRaises(XRPLModelException) as cm:
            self._batch(
                self._inner(sponsor=_SPONSOR, sponsor_flags=SponsorFlag.SPF_SPONSOR_FEE)
            )
        self.assertIn("`SPF_SPONSOR_FEE` (0x1) is not allowed", str(cm.exception))

    def test_inner_placeholder_may_not_carry_signers(self):
        """The sponsor signs through the outer BatchSigners instead."""
        with self.assertRaises(XRPLModelException) as cm:
            self._batch(
                self._inner(
                    sponsor=_SPONSOR,
                    sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
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
            )
        self.assertIn("must be an empty placeholder", str(cm.exception))

    def test_both_legal_inner_shapes_are_accepted(self):
        """Co-signed carries the empty placeholder; pre-funded omits it."""
        co_signed = self._inner(
            sponsor=_SPONSOR,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            sponsor_signature=SponsorSignature(),
        )
        pre_funded = self._inner(
            sponsor=_SPONSOR, sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE
        )
        for label, inner in (("co-signed", co_signed), ("pre-funded", pre_funded)):
            with self.subTest(shape=label):
                self.assertTrue(self._batch(inner).is_valid())
