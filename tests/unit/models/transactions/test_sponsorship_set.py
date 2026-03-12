from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.sponsorship_set import SponsorshipSet, SponsorshipSetFlag
from xrpl.models.transactions.types import TransactionType

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_ACCOUNT2 = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"


class TestSponsorshipSet(TestCase):
    def test_valid_minimal(self):
        """SponsorshipSet with just account (all fields optional)."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_all_fields(self):
        """SponsorshipSet with all fields set."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            counterparty_sponsor=_ACCOUNT2,
            sponsee=_ACCOUNT2,
            fee_amount="1000000",
            max_fee="2000000",
            reserve_count=5,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_xrp_fee_amount(self):
        """fee_amount as string (XRP drops)."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            fee_amount="1000000",
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_issued_currency_fee_amount(self):
        """fee_amount as IssuedCurrencyAmount."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            fee_amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=_ACCOUNT,
                value="10",
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_flags(self):
        """Using SponsorshipSetFlag values."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            flags=SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_combined_flags(self):
        """Using multiple SponsorshipSetFlag values combined."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            flags=(
                SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE
                | SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_valid_delete_object_flag(self):
        """Using TF_DELETE_OBJECT flag."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_counterparty_sponsor(self):
        """Setting counterparty_sponsor field."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            counterparty_sponsor=_ACCOUNT2,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_reserve_count(self):
        """Setting reserve_count."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            reserve_count=10,
        )
        self.assertTrue(tx.is_valid())

    def test_has_correct_transaction_type(self):
        """Verify transaction_type is TransactionType.SPONSORSHIP_SET."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
        )
        self.assertEqual(tx.transaction_type, TransactionType.SPONSORSHIP_SET)

    def test_valid_clear_flags(self):
        """Using clear flag variants."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            flags=SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE,
        )
        self.assertTrue(tx.is_valid())

        tx2 = SponsorshipSet(
            account=_ACCOUNT,
            flags=SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE,
        )
        self.assertTrue(tx2.is_valid())

    def test_valid_with_max_fee(self):
        """Setting max_fee as IssuedCurrencyAmount."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            max_fee=IssuedCurrencyAmount(
                currency="USD",
                issuer=_ACCOUNT,
                value="100",
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_xrp_max_fee(self):
        """Setting max_fee as XRP drops string."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            max_fee="5000000",
        )
        self.assertTrue(tx.is_valid())
