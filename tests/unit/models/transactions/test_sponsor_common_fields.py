"""Tests for sponsor common fields on Transaction base class."""

from unittest import TestCase

from xrpl.models.transactions.payment import Payment, PaymentFlag
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
