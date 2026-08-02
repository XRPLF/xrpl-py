from unittest import TestCase

from xrpl.core.binarycodec import decode, encode
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.sponsorship_transfer import (
    SponsorshipTransfer,
    SponsorshipTransferFlag,
)
from xrpl.models.transactions.transaction import Signer, SponsorFlag
from xrpl.models.transactions.types import TransactionType

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_ACCOUNT2 = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"
_OBJECT_ID = "DB303FC1C7611B22C09E773B51044F6BEA02EF917DF59A2E2860871E167066A5"

# `_ACCOUNT2` is not checksum-valid, which the model layer never checks but the
# binary codec does. Use this one in tests that encode.
_SPONSOR = "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH"


class TestSponsorshipTransfer(TestCase):
    def test_valid_minimal(self):
        """SponsorshipTransfer with just account and one operation flag.

        rippled requires exactly one of END / CREATE / REASSIGN
        (`popcount(flags & transferFlags) != 1` -> temINVALID_FLAG), so there is
        no valid flagless form.
        """
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_object_id(self):
        """Setting object_id (hex string, 64 chars)."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_sponsee(self):
        """Setting sponsee. Only valid with END; CREATE/REASSIGN reject it."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_all_fields(self):
        """Both object_id and sponsee set."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_end_flag(self):
        """Using TF_SPONSORSHIP_END flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_create_flag(self):
        """Using TF_SPONSORSHIP_CREATE flag (no sponsee — forbidden with CREATE)."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_ACCOUNT2,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_reassign_flag(self):
        """Using TF_SPONSORSHIP_REASSIGN flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_ACCOUNT2,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
        )
        self.assertTrue(tx.is_valid())

    def test_has_correct_transaction_type(self):
        """Verify transaction_type is TransactionType.SPONSORSHIP_TRANSFER."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertEqual(tx.transaction_type, TransactionType.SPONSORSHIP_TRANSFER)

    def test_valid_with_flags_and_all_fields(self):
        """All fields plus a flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertTrue(tx.is_valid())

    def test_to_dict_snake_case_fields(self):
        """to_dict() produces snake_case field names and correct values."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        d = tx.to_dict()
        self.assertEqual(d["account"], _ACCOUNT)
        self.assertEqual(d["object_id"], _OBJECT_ID)
        self.assertEqual(d["sponsee"], _ACCOUNT2)
        self.assertEqual(d["flags"], int(SponsorshipTransferFlag.TF_SPONSORSHIP_END))
        self.assertEqual(d["transaction_type"], "SponsorshipTransfer")

    def test_to_dict_omits_none_fields(self):
        """to_dict() does not include fields set to None."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        d = tx.to_dict()
        self.assertNotIn("object_id", d)
        self.assertNotIn("sponsee", d)
        self.assertNotIn("sponsor", d)
        self.assertNotIn("sponsor_flags", d)
        self.assertNotIn("sponsor_signature", d)

    def test_to_xrpl_camel_case_fields(self):
        """to_xrpl() produces CamelCase field names."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        xrpl_dict = tx.to_xrpl()
        self.assertIn("Account", xrpl_dict)
        self.assertIn("ObjectID", xrpl_dict)
        self.assertIn("Sponsee", xrpl_dict)
        self.assertIn("TransactionType", xrpl_dict)
        self.assertEqual(xrpl_dict["TransactionType"], "SponsorshipTransfer")
        self.assertNotIn("object_id", xrpl_dict)
        self.assertNotIn("sponsee", xrpl_dict)

    def test_from_dict_roundtrip(self):
        """Roundtrip through to_dict() and from_dict() preserves all fields."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_ACCOUNT2,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
        )
        roundtripped = SponsorshipTransfer.from_dict(tx.to_dict())
        self.assertEqual(roundtripped.account, tx.account)
        self.assertEqual(roundtripped.object_id, tx.object_id)
        self.assertEqual(
            roundtripped.flags,
            int(SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN),
        )

    def test_flags_interface_dict(self):
        """Flags can be expressed as a SponsorshipTransferFlagInterface dict."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            flags={"TF_SPONSORSHIP_END": True},
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(d["flags"], int(SponsorshipTransferFlag.TF_SPONSORSHIP_END))

    def test_flags_interface_dict_create(self):
        """FlagInterface dict with TF_SPONSORSHIP_CREATE (no sponsee)."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsor=_ACCOUNT2,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            flags={"TF_SPONSORSHIP_CREATE": True},
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(d["flags"], int(SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE))

    def test_flags_interface_dict_reassign(self):
        """FlagInterface dict with TF_SPONSORSHIP_REASSIGN (no sponsee)."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_ACCOUNT2,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            flags={"TF_SPONSORSHIP_REASSIGN": True},
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(
            d["flags"], int(SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN)
        )

    def test_has_flag_end(self):
        """has_flag() returns True when TF_SPONSORSHIP_END is set."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        self.assertTrue(tx.has_flag(int(SponsorshipTransferFlag.TF_SPONSORSHIP_END)))
        self.assertFalse(
            tx.has_flag(int(SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE))
        )

    def test_with_sponsor_fee_fields(self):
        """Fee sponsorship may ride alongside the required reserve flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_ACCOUNT2,
            sponsor_flags=(
                SponsorFlag.SPF_SPONSOR_FEE | SponsorFlag.SPF_SPONSOR_RESERVE
            ),
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(d["sponsor"], _ACCOUNT2)
        self.assertEqual(d["sponsor_flags"], 3)

    def test_with_sponsor_reserve_fields(self):
        """SponsorshipTransfer with sponsor covering reserve costs."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsor=_ACCOUNT2,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(d["sponsor_flags"], 2)

    def test_with_sponsor_signature(self):
        """SponsorshipTransfer with a co-signed sponsor_signature."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_ACCOUNT2,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            sponsor_signature=SponsorSignature(
                signing_pub_key="ED000000",
                txn_signature="DEADBEEF",
            ),
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertIn("sponsor_signature", d)
        self.assertEqual(d["sponsor_signature"]["signing_pub_key"], "ED000000")

    def test_with_sponsor_multisig(self):
        """SponsorshipTransfer with multi-signature sponsor."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_ACCOUNT2,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            sponsor_signature=SponsorSignature(
                signers=[
                    Signer(
                        account=_ACCOUNT2,
                        signing_pub_key="ED000000",
                        txn_signature="DEADBEEF",
                    )
                ]
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_flag_enum_values(self):
        """Verify SponsorshipTransferFlag enum values match the spec."""
        self.assertEqual(int(SponsorshipTransferFlag.TF_SPONSORSHIP_END), 0x00010000)
        self.assertEqual(int(SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE), 0x00020000)
        self.assertEqual(
            int(SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN), 0x00040000
        )

    def test_immutable_frozen_dataclass(self):
        """SponsorshipTransfer is frozen; mutating fields raises AttributeError."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
        )
        with self.assertRaises(AttributeError):
            tx.sponsee = _ACCOUNT2  # type: ignore[misc]

    def test_invalid_no_operation_flag(self):
        """Zero operation flags is malformed, not a valid "no-op" form.

        rippled: `popcount(tx.getFlags() & transferFlags) != 1` ->
        temINVALID_FLAG. A flagless SponsorshipTransfer names no operation to
        perform, so the model must reject it rather than let the server do it.
        """
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                object_id=_OBJECT_ID,
            )
        self.assertIn("Exactly one of", str(cm.exception))

    def test_integer_flag_value(self):
        """Passing an integer directly as flags is accepted."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            flags=0x00010000,
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.to_dict()["flags"], 0x00010000)

    # ------------------------------------------------------------------ #
    #  SponsorshipTransfer flag validation                                #
    # ------------------------------------------------------------------ #

    _MULTI_FLAG_MSG = (
        "Exactly one of `TF_SPONSORSHIP_END`, `TF_SPONSORSHIP_CREATE`, or "
        "`TF_SPONSORSHIP_REASSIGN` must be set."
    )
    _SPONSEE_FLAG_MSG = (
        "`sponsee` cannot be set when `TF_SPONSORSHIP_CREATE` is active."
    )

    def test_invalid_end_and_create_flags(self):
        """Setting TF_SPONSORSHIP_END and TF_SPONSORSHIP_CREATE together is rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                flags=(
                    SponsorshipTransferFlag.TF_SPONSORSHIP_END
                    | SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE
                ),
            )
        self.assertIn(self._MULTI_FLAG_MSG, str(cm.exception))

    def test_invalid_end_and_reassign_flags(self):
        """END and REASSIGN together is rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                flags=(
                    SponsorshipTransferFlag.TF_SPONSORSHIP_END
                    | SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN
                ),
            )
        self.assertIn(self._MULTI_FLAG_MSG, str(cm.exception))

    def test_invalid_create_and_reassign_flags(self):
        """CREATE and REASSIGN together is rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                flags=(
                    SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE
                    | SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN
                ),
            )
        self.assertIn(self._MULTI_FLAG_MSG, str(cm.exception))

    def test_invalid_sponsee_with_create_flag(self):
        """sponsee must not be set when TF_SPONSORSHIP_CREATE is active."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                object_id=_OBJECT_ID,
                sponsee=_ACCOUNT2,
                flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            )
        self.assertIn(self._SPONSEE_FLAG_MSG, str(cm.exception))

    def test_invalid_sponsee_with_reassign_flag(self):
        """sponsee must not be set when TF_SPONSORSHIP_REASSIGN is active."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                object_id=_OBJECT_ID,
                sponsee=_ACCOUNT2,
                flags=SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
            )
        self.assertIn(
            "`sponsee` cannot be set when `TF_SPONSORSHIP_REASSIGN` is active.",
            str(cm.exception),
        )

    # ------------------------------------------------------------------ #
    #  Transaction-level sponsor cross-field validation                   #
    # ------------------------------------------------------------------ #

    def test_invalid_sponsor_equals_account(self):
        """sponsor identical to account must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor=_ACCOUNT,
            )
        self.assertIn("`sponsor` must differ from `account`.", str(cm.exception))

    def test_invalid_sponsor_flags_without_sponsor(self):
        """sponsor_flags without sponsor must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor_flags=0x00000001,
            )
        self.assertIn(
            "`sponsor_flags` requires `sponsor` to be set.", str(cm.exception)
        )

    def test_invalid_sponsor_signature_without_sponsor(self):
        """sponsor_signature without sponsor must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor_signature=SponsorSignature(
                    signing_pub_key="ED000000",
                    txn_signature="DEADBEEF",
                ),
            )
        self.assertIn(
            "`sponsor_signature` requires `sponsor` to be set.", str(cm.exception)
        )

    def test_invalid_sponsor_flags_bad_bits(self):
        """sponsor_flags with bits beyond 0x3 must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor=_ACCOUNT2,
                sponsor_flags=0x00000004,  # bit 2 — outside allowed 0x1|0x2
            )
        self.assertIn(
            "`sponsor_flags` may only use bits 0x1 (spfSponsorFee) "
            "and 0x2 (spfSponsorReserve).",
            str(cm.exception),
        )

    def test_invalid_sponsor_flags_combined_bad_bits(self):
        """sponsor_flags mixing valid and invalid bits must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsor=_ACCOUNT2,
                sponsor_flags=0x00000007,  # 0x1 | 0x2 | 0x4
            )
        self.assertIn(
            "`sponsor_flags` may only use bits 0x1 (spfSponsorFee) "
            "and 0x2 (spfSponsorReserve).",
            str(cm.exception),
        )

    # ------------------------------------------------------------------ #
    #  Operation-specific field rules                                      #
    # ------------------------------------------------------------------ #

    def test_create_and_reassign_require_a_sponsor(self):
        """Both name an incoming sponsor, so `sponsor` is mandatory.

        rippled: `!isFieldPresent(sfSponsor)` -> temMALFORMED.
        """
        for flag in (
            SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
        ):
            with self.subTest(flag=flag.name):
                with self.assertRaises(XRPLModelException) as cm:
                    SponsorshipTransfer(
                        account=_ACCOUNT, object_id=_OBJECT_ID, flags=flag
                    )
                self.assertIn("`sponsor` is required", str(cm.exception))

    def test_create_and_reassign_require_the_reserve_flag(self):
        """Fee-only sponsorship cannot transfer a reserve.

        rippled: `!isReserveSponsored(tx)` -> temINVALID_FLAG.
        """
        for flag in (
            SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
        ):
            with self.subTest(flag=flag.name):
                with self.assertRaises(XRPLModelException) as cm:
                    SponsorshipTransfer(
                        account=_ACCOUNT,
                        object_id=_OBJECT_ID,
                        sponsor=_ACCOUNT2,
                        sponsor_flags=SponsorFlag.SPF_SPONSOR_FEE,
                        flags=flag,
                    )
                self.assertIn("SPF_SPONSOR_RESERVE", str(cm.exception))

    def test_end_rejects_a_sponsor(self):
        """Ending removes a sponsor rather than naming one (temMALFORMED)."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                object_id=_OBJECT_ID,
                sponsor=_ACCOUNT2,
                sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
                flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
            )
        self.assertIn("cannot be set when `TF_SPONSORSHIP_END`", str(cm.exception))

    def test_end_rejects_sponsee_equal_to_account(self):
        """`sponsee == account` is redundant and rejected (temMALFORMED)."""
        with self.assertRaises(XRPLModelException) as cm:
            SponsorshipTransfer(
                account=_ACCOUNT,
                sponsee=_ACCOUNT,
                flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
            )
        self.assertIn("`sponsee` must differ from `account`", str(cm.exception))

    def test_every_field_survives_the_binary_codec(self):
        """Model validation says a field is accepted, not that it is sendable.

        Each field is serialized separately, so a populated instance of every
        one is the only way to know the whole transaction reaches the wire.
        """
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_SPONSOR,
            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
            fee="10",
            sequence=1,
            signing_pub_key="",
        )
        source = tx.to_xrpl()
        self.assertEqual(decode(encode(source)), source)
