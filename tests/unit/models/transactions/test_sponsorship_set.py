from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.amounts.mpt_amount import MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.sponsorship_set import SponsorshipSet, SponsorshipSetFlag
from xrpl.models.transactions.types import TransactionType

_MPT_ISSUANCE_ID = "000004C463C52827307480341125DA0577DEFC38"

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_ACCOUNT2 = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"
_ACCOUNT3 = "rN7n7otQDd6FczFgLdlqtyMVrn3HMfXpf"


class TestSponsorshipSet(TestCase):
    # ------------------------------------------------------------------ #
    #  Valid cases                                                         #
    # ------------------------------------------------------------------ #

    def test_valid_minimal(self):
        """Sponsor submits with only the sponsee field."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_all_fields(self):
        """Sponsor submits with sponsee and every optional field set."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            fee_amount="1000000",
            max_fee="2000000",
            reserve_count=5,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_xrp_fee_amount(self):
        """fee_amount as XRP drops string."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            fee_amount="1000000",
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_xrp_max_fee(self):
        """max_fee as XRP drops string."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            max_fee="5000000",
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
        """Two non-conflicting flags combined."""
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
        """TF_DELETE_OBJECT alone with a sponsee is valid."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_counterparty_sponsor(self):
        """Sponsee submits, providing counterparty_sponsor (deletion scenario)."""
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
            sponsee=_ACCOUNT2,
        )
        self.assertEqual(tx.transaction_type, TransactionType.SPONSORSHIP_SET)

    def test_valid_clear_flags(self):
        """Using clear flag variants (no conflict)."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            flags=SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE,
        )
        self.assertTrue(tx.is_valid())

        tx2 = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            flags=SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE,
        )
        self.assertTrue(tx2.is_valid())

    def test_valid_delete_with_counterparty_sponsor(self):
        """Sponsee deletes using counterparty_sponsor + TF_DELETE_OBJECT."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            counterparty_sponsor=_ACCOUNT2,
            flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
        )
        self.assertTrue(tx.is_valid())

    # ------------------------------------------------------------------ #
    #  Concern 1 — fee_amount / max_fee must be XRP (not IOU or MPT)     #
    # ------------------------------------------------------------------ #

    _FEE_AMOUNT_MSG = (
        "`fee_amount` must be XRP drops (a string), "
        "not an issued currency or MPT amount."
    )
    _MAX_FEE_MSG = (
        "`max_fee` must be XRP drops (a string), "
        "not an issued currency or MPT amount."
    )

    def test_invalid_fee_amount_iou(self):
        """fee_amount as IssuedCurrencyAmount is rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                fee_amount=IssuedCurrencyAmount(
                    currency="USD",
                    issuer=_ACCOUNT,
                    value="10",
                ),
            )
        self.assertIn(self._FEE_AMOUNT_MSG, str(cm.exception))

    def test_invalid_max_fee_iou(self):
        """max_fee as IssuedCurrencyAmount must be rejected with the correct message."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                max_fee=IssuedCurrencyAmount(
                    currency="USD",
                    issuer=_ACCOUNT,
                    value="100",
                ),
            )
        self.assertIn(self._MAX_FEE_MSG, str(cm.exception))

    def test_invalid_fee_amount_mpt(self):
        """fee_amount as MPTAmount must be rejected with the correct message."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                fee_amount=MPTAmount(
                    mpt_issuance_id=_MPT_ISSUANCE_ID,
                    value="100",
                ),
            )
        self.assertIn(self._FEE_AMOUNT_MSG, str(cm.exception))

    def test_invalid_max_fee_mpt(self):
        """max_fee as MPTAmount must be rejected with the correct message."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                max_fee=MPTAmount(
                    mpt_issuance_id=_MPT_ISSUANCE_ID,
                    value="100",
                ),
            )
        self.assertIn(self._MAX_FEE_MSG, str(cm.exception))

    # ------------------------------------------------------------------ #
    #  Concern 2 — XOR: exactly one of counterparty_sponsor / sponsee     #
    # ------------------------------------------------------------------ #

    _XOR_MSG = (
        "Exactly one of `counterparty_sponsor` or `sponsee` must be present "
        "(not both, not neither)."
    )

    def test_invalid_neither_counterparty_nor_sponsee(self):
        """Providing neither counterparty_sponsor nor sponsee must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(account=_ACCOUNT)
        self.assertIn(self._XOR_MSG, str(cm.exception))

    def test_invalid_both_counterparty_and_sponsee(self):
        """Providing both counterparty_sponsor and sponsee must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                counterparty_sponsor=_ACCOUNT2,
                sponsee=_ACCOUNT3,
            )
        self.assertIn(self._XOR_MSG, str(cm.exception))

    def test_invalid_sponsee_equals_account(self):
        """sponsee identical to account must be rejected with the correct message."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT,
            )
        self.assertIn("`sponsee` must differ from `account`.", str(cm.exception))

    def test_invalid_counterparty_sponsor_equals_account(self):
        """counterparty_sponsor identical to account must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                counterparty_sponsor=_ACCOUNT,
            )
        self.assertIn(
            "`counterparty_sponsor` must differ from `account`.", str(cm.exception)
        )

    # ------------------------------------------------------------------ #
    #  Concern 3 — mutually exclusive flag combinations                   #
    # ------------------------------------------------------------------ #

    def test_invalid_set_and_clear_fee_flags(self):
        """SET and CLEAR require-sign-for-fee flags are mutually exclusive."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                flags=(
                    SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE
                    | SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE
                ),
            )
        self.assertIn(
            "`TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE` and "
            "`TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE` are mutually exclusive.",
            str(cm.exception),
        )

    def test_invalid_set_and_clear_reserve_flags(self):
        """SET and CLEAR require-sign-for-reserve flags are mutually exclusive."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                flags=(
                    SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE
                    | SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE
                ),
            )
        self.assertIn(
            "`TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE` and "
            "`TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE` are mutually exclusive.",
            str(cm.exception),
        )

    def test_invalid_delete_with_set_fee_flag(self):
        """TF_DELETE_OBJECT can't combine with set fee flag."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                flags=(
                    SponsorshipSetFlag.TF_DELETE_OBJECT
                    | SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE
                ),
            )
        self.assertIn(
            "`TF_DELETE_OBJECT` cannot be combined with any set/clear flags.",
            str(cm.exception),
        )

    def test_invalid_delete_with_clear_reserve_flag(self):
        """TF_DELETE_OBJECT can't combine with clear reserve flag."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                flags=(
                    SponsorshipSetFlag.TF_DELETE_OBJECT
                    | SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE
                ),
            )
        self.assertIn(
            "`TF_DELETE_OBJECT` cannot be combined with any set/clear flags.",
            str(cm.exception),
        )
