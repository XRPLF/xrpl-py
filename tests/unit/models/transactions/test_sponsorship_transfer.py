from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.sponsorship_transfer import (
    SponsorshipTransfer,
    SponsorshipTransferFlag,
)
from xrpl.models.transactions.transaction import Signer
from xrpl.models.transactions.types import TransactionType

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_ACCOUNT2 = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"
_OBJECT_ID = "DB303FC1C7611B22C09E773B51044F6BEA02EF917DF59A2E2860871E167066A5"


class TestSponsorshipTransfer(TestCase):
    def test_valid_minimal(self):
        """SponsorshipTransfer with just account."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_object_id(self):
        """Setting object_id (hex string, 64 chars)."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_sponsee(self):
        """Setting sponsee."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_all_fields(self):
        """Both object_id and sponsee set."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
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
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_reassign_flag(self):
        """Using TF_SPONSORSHIP_REASSIGN flag."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
        )
        self.assertTrue(tx.is_valid())

    def test_has_correct_transaction_type(self):
        """Verify transaction_type is TransactionType.SPONSORSHIP_TRANSFER."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
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
        )
        d = tx.to_dict()
        self.assertNotIn("object_id", d)
        self.assertNotIn("sponsee", d)
        self.assertNotIn("flags", d)
        self.assertNotIn("sponsor", d)
        self.assertNotIn("sponsor_flags", d)
        self.assertNotIn("sponsor_signature", d)

    def test_to_xrpl_camel_case_fields(self):
        """to_xrpl() produces CamelCase field names."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
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
        """SponsorshipTransfer with sponsor and sponsor_flags (fee sponsorship)."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsor=_ACCOUNT2,
            sponsor_flags=0x00000001,  # tfSponsorFee
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(d["sponsor"], _ACCOUNT2)
        self.assertEqual(d["sponsor_flags"], 1)

    def test_with_sponsor_reserve_fields(self):
        """SponsorshipTransfer with sponsor covering reserve costs."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            sponsee=_ACCOUNT2,
            sponsor=_ACCOUNT2,
            sponsor_flags=0x00000002,  # tfSponsorReserve
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(d["sponsor_flags"], 2)

    def test_with_sponsor_signature(self):
        """SponsorshipTransfer with a co-signed sponsor_signature."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
            sponsee=_ACCOUNT2,
            sponsor=_ACCOUNT2,
            sponsor_flags=0x00000001,
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
            sponsor_flags=0x00000001,
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
        self.assertEqual(int(SponsorshipTransferFlag.TF_SPONSORSHIP_END), 0x00000001)
        self.assertEqual(int(SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE), 0x00000002)
        self.assertEqual(
            int(SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN), 0x00000004
        )

    def test_immutable_frozen_dataclass(self):
        """SponsorshipTransfer is frozen; mutating fields raises AttributeError."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
        )
        with self.assertRaises(AttributeError):
            tx.sponsee = _ACCOUNT2  # type: ignore[misc]

    def test_no_flags_in_dict_when_none(self):
        """flags key is absent from to_dict() when no flags are set."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            object_id=_OBJECT_ID,
        )
        d = tx.to_dict()
        self.assertNotIn("flags", d)

    def test_integer_flag_value(self):
        """Passing an integer directly as flags is accepted."""
        tx = SponsorshipTransfer(
            account=_ACCOUNT,
            flags=0x00000001,
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.to_dict()["flags"], 1)

    # ------------------------------------------------------------------ #
    #  Concern 4 — SponsorshipTransfer flag validation                    #
    # ------------------------------------------------------------------ #

    _MULTI_FLAG_MSG = (
        "Exactly one of `TF_SPONSORSHIP_END`, `TF_SPONSORSHIP_CREATE`, or "
        "`TF_SPONSORSHIP_REASSIGN` may be set at a time."
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

    # ------------------------------------------------------------------ #
    #  Concern 5 — Transaction-level sponsor cross-field validation       #
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
            "`sponsor_flags` may only use bits 0x1 (tfSponsorFee) "
            "and 0x2 (tfSponsorReserve).",
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
            "`sponsor_flags` may only use bits 0x1 (tfSponsorFee) "
            "and 0x2 (tfSponsorReserve).",
            str(cm.exception),
        )
