from unittest import TestCase

from xrpl.core.binarycodec import decode, encode
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
        """Sponsor submits with a sponsee and one budget delta.

        A SponsorshipSet that is not deleting must actually change something --
        rippled returns temREDUNDANT when no delta, `max_fee`, or sponsorship
        flag is present -- so there is no valid field-free form.
        """
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            fee_amount_delta="1000000",
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_no_modification(self):
        """Neither a delta, `max_fee`, nor a flag means the tx does nothing."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
            )
        self.assertIn("must set at least one of", str(cm.exception))

    def test_valid_all_fields(self):
        """Sponsor submits with sponsee and every optional field set."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            fee_amount_delta="1000000",
            max_fee="2000000",
            remaining_owner_count_delta=5,
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
            flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_remaining_owner_count(self):
        """Setting remaining_owner_count_delta."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            remaining_owner_count_delta=10,
        )
        self.assertTrue(tx.is_valid())

    def test_has_correct_transaction_type(self):
        """Verify transaction_type is TransactionType.SPONSORSHIP_SET."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            fee_amount_delta="1000000",
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

    # ------------------------------------------------------------------ #
    #  fee_amount_delta / max_fee must be XRP (not IOU or MPT)                 #
    # ------------------------------------------------------------------ #

    _FEE_AMOUNT_MSG = (
        "`fee_amount_delta` must be XRP drops (a string), "
        "not an issued currency or MPT amount."
    )
    _MAX_FEE_MSG = (
        "`max_fee` must be XRP drops (a string), "
        "not an issued currency or MPT amount."
    )

    # ------------------------------------------------------------------ #
    #  XOR: exactly one of counterparty_sponsor / sponsee                 #
    # ------------------------------------------------------------------ #

    _XOR_MSG = (
        "Exactly one of `counterparty_sponsor` or `sponsee` must be present "
        "(not both, not neither)."
    )

    def test_invalid_non_xrp_amounts(self):
        """Both amount fields are XRP drops; neither accepts IOU or MPT."""
        amounts = {
            "IOU": IssuedCurrencyAmount(currency="USD", issuer=_ACCOUNT, value="10"),
            "MPT": MPTAmount(mpt_issuance_id=_MPT_ISSUANCE_ID, value="100"),
        }
        fields = {
            "fee_amount_delta": self._FEE_AMOUNT_MSG,
            "max_fee": self._MAX_FEE_MSG,
        }
        for field, message in fields.items():
            for kind, amount in amounts.items():
                with self.subTest(field=field, amount=kind):
                    with self.assertRaises(XRPLModelException) as cm:
                        SponsorshipSet(
                            account=_ACCOUNT, sponsee=_ACCOUNT2, **{field: amount}
                        )
                    self.assertIn(message, str(cm.exception))

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
    #  Mutually exclusive flag combinations                               #
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    #  counterparty_sponsor only valid when deleting                      #
    # ------------------------------------------------------------------ #

    def test_invalid_set_and_clear_the_same_budget(self):
        """Setting and clearing one budget's require-sign flag contradicts itself."""
        for budget in ("FEE", "RESERVE"):
            with self.subTest(budget=budget):
                set_flag = getattr(
                    SponsorshipSetFlag, f"TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_{budget}"
                )
                clear_flag = getattr(
                    SponsorshipSetFlag,
                    f"TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_{budget}",
                )
                with self.assertRaises(XRPLModelException) as cm:
                    SponsorshipSet(
                        account=_ACCOUNT,
                        sponsee=_ACCOUNT2,
                        flags=set_flag | clear_flag,
                    )
                self.assertIn(
                    f"`{set_flag.name}` and `{clear_flag.name}` are mutually "
                    "exclusive.",
                    str(cm.exception),
                )

    def test_invalid_delete_combined_with_any_set_or_clear_flag(self):
        """Deleting the object leaves nothing for a flag to apply to."""
        for flag in (
            SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE,
            SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE,
            SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE,
            SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE,
        ):
            with self.subTest(flag=flag.name):
                with self.assertRaises(XRPLModelException) as cm:
                    SponsorshipSet(
                        account=_ACCOUNT,
                        sponsee=_ACCOUNT2,
                        flags=SponsorshipSetFlag.TF_DELETE_OBJECT | flag,
                    )
                self.assertIn(
                    "`TF_DELETE_OBJECT` cannot be combined with any set/clear "
                    "flags.",
                    str(cm.exception),
                )

    def test_invalid_delete_with_a_modification_field(self):
        """A delete carries no budget changes (rippled: temMALFORMED)."""
        for field, value in (
            ("fee_amount_delta", "1000000"),
            ("max_fee", "1000000"),
            ("remaining_owner_count_delta", 3),
        ):
            with self.subTest(field=field):
                with self.assertRaises(XRPLModelException) as cm:
                    SponsorshipSet(
                        account=_ACCOUNT,
                        sponsee=_ACCOUNT2,
                        flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
                        **{field: value},
                    )
                self.assertIn("TF_DELETE_OBJECT", str(cm.exception))
                self.assertIn(field, str(cm.exception))

    def test_invalid_counterparty_sponsor_without_delete(self):
        """counterparty_sponsor without TF_DELETE_OBJECT must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                counterparty_sponsor=_ACCOUNT2,
            )
        self.assertIn(
            "`counterparty_sponsor` can only be used together with "
            "`TF_DELETE_OBJECT`",
            str(cm.exception),
        )

    # ------------------------------------------------------------------ #
    #  Delete forbids fee_amount_delta/max_fee/remaining_owner_count_delta      #
    # ------------------------------------------------------------------ #

    def test_simultaneous_flag_conflicts_are_all_reported(self):
        """Each mutually-exclusive pair reports under its own key.

        A shared `errors["flags"]` key let later checks overwrite earlier ones, so
        a transaction violating several rules surfaced only the last, sending the
        caller round a fix-and-rediscover loop.
        """
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                flags=(
                    SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE
                    | SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE
                    | SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE
                    | SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_RESERVE
                ),
            )
        message = str(cm.exception)
        self.assertIn("TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE", message)
        self.assertIn("TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE", message)

    def test_delete_object_conflict_reported_alongside_pair_conflict(self):
        """TF_DELETE_OBJECT's conflict does not mask a set/clear pair conflict."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                flags=(
                    SponsorshipSetFlag.TF_DELETE_OBJECT
                    | SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE
                    | SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE
                ),
            )
        message = str(cm.exception)
        self.assertIn("TF_DELETE_OBJECT", message)
        self.assertIn("TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE", message)

    # ------------------------------------------------------------------ #
    #  Delta semantics                                                   #
    # ------------------------------------------------------------------ #

    def test_negative_fee_amount_delta_is_valid(self):
        """A negative delta refunds budget to the sponsor, so it is legal.

        rippled clamps the refund so the budget cannot go below zero; only zero
        is rejected, as a no-op.
        """
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            fee_amount_delta="-500000",
        )
        self.assertTrue(tx.is_valid())

    def test_negative_deltas_round_trip_through_the_binary_codec(self):
        """Model validation alone does not prove a negative delta is sendable.

        ``FeeAmountDelta`` is an ``Amount``, and XRP amounts encode the sign as a
        flag bit rather than two's complement, so a negative value exercises a
        separate code path from a positive one.
        """
        # Encoding checksums addresses, which model validation does not, so use
        # real ones rather than the module's placeholder constants.
        tx = SponsorshipSet(
            account="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
            sponsee="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
            fee_amount_delta="-500000",
            remaining_owner_count_delta=-2,
            fee="10",
            sequence=1,
            signing_pub_key="",
        )
        decoded = decode(encode(tx.to_xrpl()))
        self.assertEqual(decoded["FeeAmountDelta"], "-500000")
        self.assertEqual(decoded["RemainingOwnerCountDelta"], -2)

    def test_negative_remaining_owner_count_delta_is_valid(self):
        """RemainingOwnerCountDelta is a signed Int32; negative reduces budget."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            remaining_owner_count_delta=-2,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_zero_fee_amount_delta(self):
        """Zero has no effect -> temBAD_AMOUNT."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                fee_amount_delta="0",
            )
        self.assertIn("must be non-zero", str(cm.exception))

    def test_invalid_zero_remaining_owner_count_delta(self):
        """Zero has no effect -> temINVALID."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                remaining_owner_count_delta=0,
            )
        self.assertIn("must be non-zero", str(cm.exception))

    def test_invalid_negative_max_fee(self):
        """`max_fee` is an absolute cap, not a delta -> temBAD_AMOUNT."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipSet(
                account=_ACCOUNT,
                sponsee=_ACCOUNT2,
                max_fee="-1",
                fee_amount_delta="1000000",
            )
        self.assertIn("must not be negative", str(cm.exception))

    def test_delta_fields_serialize_with_new_names(self):
        """The wire names are FeeAmountDelta / RemainingOwnerCountDelta."""
        tx = SponsorshipSet(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            fee_amount_delta="1000000",
            remaining_owner_count_delta=-4,
        )
        xrpl_dict = tx.to_xrpl()
        self.assertEqual(xrpl_dict["FeeAmountDelta"], "1000000")
        self.assertEqual(xrpl_dict["RemainingOwnerCountDelta"], -4)
        self.assertNotIn("FeeAmount", xrpl_dict)
        self.assertNotIn("RemainingOwnerCount", xrpl_dict)

    def test_every_field_survives_the_binary_codec(self):
        """Both addressing forms, with every optional field populated."""
        shapes = {
            "sponsee": dict(
                sponsee="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
                fee_amount_delta="-500000",
                max_fee="100000",
                remaining_owner_count_delta=-2,
            ),
            "counterparty_sponsor": dict(
                counterparty_sponsor="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
                flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
            ),
        }
        for label, fields in shapes.items():
            with self.subTest(shape=label):
                tx = SponsorshipSet(
                    account="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                    fee="10",
                    sequence=1,
                    signing_pub_key="",
                    **fields,
                )
                source = tx.to_xrpl()
                self.assertEqual(decode(encode(source)), source)
