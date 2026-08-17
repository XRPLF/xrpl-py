"""Model-layer tests for XLS-68 sponsorship.

Three concerns, one per class group:

* the sponsorship fields shared by every transaction (`sponsor`,
  `sponsor_flags`, `sponsor_signature`), including the Batch inner rules;
* the `SponsorSignature` field's own shapes and wire-format invariants;
* a broad check that every shape rippled accepts still constructs.

Producing real signatures and autofilling fees live one layer up, in
`tests/unit/transaction/` and `tests/unit/asyn/transaction/`.
"""

from unittest import TestCase

from xrpl.core.binarycodec import decode, encode, encode_for_signing
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import (
    Batch,
    CheckCreate,
    Payment,
    PaymentFlag,
    SponsorFlag,
    SponsorshipSet,
    SponsorshipTransfer,
    SponsorSignature,
    TrustSet,
)
from xrpl.models.transactions.pseudo_transactions import EnableAmendment
from xrpl.models.transactions.sponsorship_set import SponsorshipSetFlag
from xrpl.models.transactions.sponsorship_transfer import SponsorshipTransferFlag
from xrpl.models.transactions.transaction import Signer, TransactionFlag

# All checksum-valid. Model validation never checks the checksum but the binary
# codec does, so tests that encode need real addresses -- see _UNCHECKSUMMED.
_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_SPONSOR = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
_SPONSEE = "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH"
_DESTINATION = "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"

# Deliberately not checksum-valid: proves the model layer accepts it.
_UNCHECKSUMMED = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"

_OBJECT_ID = "DB303FC1C7611B22C09E773B51044F6BEA02EF917DF59A2E2860871E167066A5"
_SIGNING_PUB_KEY = "ED5F5AC43F527AE97194AC44903F8E0397F1B8AFDC25990B3B8F093E2D1D8B0E2D"
_TXN_SIGNATURE = (
    "304402203B9B0B6E0735AD5F370B2B0B3A81CDE62CC5B7C3"
    "3C5B15C76C3E4B8A0CEEF10220523D4C16C3F68C0840F1B1"
    "F4BF7D5F1C6D3DA2F9D0E4EB7A4E6BF1C3A5D7E9"
)

_FEE = SponsorFlag.SPF_SPONSOR_FEE
_RESERVE = SponsorFlag.SPF_SPONSOR_RESERVE
_IOU = IssuedCurrencyAmount(currency="USD", issuer=_SPONSOR, value="10")

# An inner Batch transaction is unsigned and pays no fee of its own.
_INNER = {"fee": "0", "sequence": 1, "signing_pub_key": "", "flags": 0x40000000}


class TestSponsorCommonFields(TestCase):
    def test_payment_sponsor_fields_serialize(self):
        """Each accepted flag value survives into the serialized form."""
        for flags in (
            SponsorFlag.SPF_SPONSOR_FEE,
            SponsorFlag.SPF_SPONSOR_RESERVE,
            SponsorFlag.SPF_SPONSOR_FEE | SponsorFlag.SPF_SPONSOR_RESERVE,
        ):
            with self.subTest(sponsor_flags=int(flags)):
                tx = Payment(
                    account=_ACCOUNT,
                    destination=_DESTINATION,
                    amount="1000000",
                    sponsor=_SPONSOR,
                    sponsor_flags=flags,
                )
                self.assertTrue(tx.is_valid())
                self.assertEqual(tx.to_dict()["sponsor"], _SPONSOR)
                self.assertEqual(tx.to_dict()["sponsor_flags"], int(flags))

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
        """An outer Batch creates no objects, so it has no reserve to sponsor.

        Rejected whether reserve is requested alone or alongside a fee.
        """
        for flags in (
            SponsorFlag.SPF_SPONSOR_RESERVE,
            SponsorFlag.SPF_SPONSOR_FEE | SponsorFlag.SPF_SPONSOR_RESERVE,
        ):
            with self.subTest(sponsor_flags=int(flags)):
                with self.assertRaises(XRPLModelException) as cm:
                    self._batch(sponsor=_SPONSOR, sponsor_flags=flags)
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

    def test_non_integer_sponsor_flags_is_a_model_error(self):
        """A non-int must surface as XRPLModelException, not a raw TypeError.

        The value reaches a bitwise `&` in validation, so an unguarded non-int
        would crash with TypeError before any error is recorded.
        """
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount="1",
                sponsor=_SPONSOR,
                sponsor_flags="not-an-int",
            )
        self.assertIn("must be an integer", str(cm.exception))


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

    def test_inner_placeholder_must_be_empty(self):
        """Populating ANY field of the placeholder is rejected; the sponsor
        signs through the outer BatchSigners instead (rippled: temBAD_SIGNER).
        """
        populated = {
            "single-sig": SponsorSignature(
                signing_pub_key="ED000000", txn_signature="DEADBEEF"
            ),
            "multi-sig": SponsorSignature(
                signers=[
                    Signer(
                        account=_SPONSOR,
                        signing_pub_key="ED000000",
                        txn_signature="DEADBEEF",
                    )
                ]
            ),
        }
        for shape, sponsor_signature in populated.items():
            with self.subTest(shape=shape):
                with self.assertRaises(XRPLModelException) as cm:
                    self._batch(
                        self._inner(
                            sponsor=_SPONSOR,
                            sponsor_flags=SponsorFlag.SPF_SPONSOR_RESERVE,
                            sponsor_signature=sponsor_signature,
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
                    account=_UNCHECKSUMMED,
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
                    account=_UNCHECKSUMMED,
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

    def test_empty_signers_array_is_rejected(self):
        """`signers=[]` is malformed -- distinct from the empty placeholder.

        The placeholder is `signers=None` (serialized `{}`); a present-but-empty
        array serializes `{"Signers": []}`, which rippled rejects
        (`kMinMultiSigners == 1`).
        """
        with self.assertRaises(XRPLModelException) as cm:
            SponsorSignature(signers=[])
        self.assertIn("`signers` must not be empty", str(cm.exception))

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
                        account=_UNCHECKSUMMED,
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


def _inner_payment(account, **overrides):
    return Payment(
        account=account, destination=_DESTINATION, amount="1", **_INNER, **overrides
    )


def _batch(*inners, **overrides):
    return Batch(
        account=_ACCOUNT,
        fee="20",
        sequence=1,
        flags=0x00010000,
        raw_transactions=list(inners),
        **overrides,
    )


class TestSponsorValidShapesAreNotBlocked(TestCase):
    def _accepts(self, cases):
        for label, build in cases.items():
            with self.subTest(shape=label):
                self.assertTrue(build().is_valid())

    def test_sponsor_common_fields(self):
        """Either sponsorship type, alone or combined."""
        self._accepts(
            {
                "fee only": lambda: Payment(
                    account=_ACCOUNT,
                    destination=_SPONSEE,
                    amount="1",
                    sponsor=_SPONSOR,
                    sponsor_flags=_FEE,
                ),
                "reserve only": lambda: Payment(
                    account=_ACCOUNT,
                    destination=_SPONSEE,
                    amount="1",
                    sponsor=_SPONSOR,
                    sponsor_flags=_RESERVE,
                ),
                "both": lambda: Payment(
                    account=_ACCOUNT,
                    destination=_SPONSEE,
                    amount="1",
                    sponsor=_SPONSOR,
                    sponsor_flags=_FEE | _RESERVE,
                ),
                # The enum is a convenience, not a requirement.
                "raw int": lambda: Payment(
                    account=_ACCOUNT,
                    destination=_SPONSEE,
                    amount="1",
                    sponsor=_SPONSOR,
                    sponsor_flags=3,
                ),
                # Only *reserve* sponsorship conflicts with delegation.
                "delegate + fee": lambda: Payment(
                    account=_ACCOUNT,
                    destination=_SPONSEE,
                    amount="1",
                    delegate=_SPONSOR,
                    sponsor=_DESTINATION,
                    sponsor_flags=_FEE,
                ),
                "reserve on TrustSet": lambda: TrustSet(
                    account=_ACCOUNT,
                    limit_amount=_IOU,
                    sponsor=_SPONSOR,
                    sponsor_flags=_RESERVE,
                ),
                "reserve on CheckCreate": lambda: CheckCreate(
                    account=_ACCOUNT,
                    destination=_SPONSEE,
                    send_max="1",
                    sponsor=_SPONSOR,
                    sponsor_flags=_RESERVE,
                ),
            }
        )

    def test_sponsor_signature_shapes(self):
        """Single-signed, multi-signed, and the empty Batch placeholder."""
        base = {
            "account": _ACCOUNT,
            "destination": _SPONSEE,
            "amount": "1",
            "sponsor": _SPONSOR,
            "sponsor_flags": _FEE,
        }
        self._accepts(
            {
                "single-signed": lambda: Payment(
                    **base,
                    sponsor_signature=SponsorSignature(
                        signing_pub_key="ED000000", txn_signature="DEADBEEF"
                    ),
                ),
                "multi-signed": lambda: Payment(
                    **base,
                    sponsor_signature=SponsorSignature(
                        signers=[
                            Signer(
                                account=_SPONSOR,
                                signing_pub_key="ED000000",
                                txn_signature="DEADBEEF",
                            )
                        ]
                    ),
                ),
            }
        )

    def test_payment_sponsor_created_account(self):
        """The flag needs plain XRP, but does not forbid ordinary sponsorship."""
        self._accepts(
            {
                "plain XRP": lambda: Payment(
                    account=_ACCOUNT,
                    destination=_SPONSEE,
                    amount="1000000",
                    flags=PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT,
                ),
                "with a fee sponsor": lambda: Payment(
                    account=_ACCOUNT,
                    destination=_SPONSEE,
                    amount="1000000",
                    flags=PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT,
                    sponsor=_SPONSOR,
                    sponsor_flags=_FEE,
                ),
                # The routing restrictions apply only under the flag.
                "issued currency, no flag": lambda: Payment(
                    account=_ACCOUNT,
                    destination=_SPONSEE,
                    amount=_IOU,
                    send_max=_IOU,
                ),
            }
        )

    def test_sponsorship_set(self):
        """Deltas of either sign, every flag combination, both delete forms."""
        sponsee = {"account": _ACCOUNT, "sponsee": _SPONSEE}
        self._accepts(
            {
                "positive fee delta": lambda: SponsorshipSet(
                    **sponsee, fee_amount_delta="1000000"
                ),
                "negative fee delta": lambda: SponsorshipSet(
                    **sponsee, fee_amount_delta="-1000000"
                ),
                "positive count delta": lambda: SponsorshipSet(
                    **sponsee, remaining_owner_count_delta=3
                ),
                "negative count delta": lambda: SponsorshipSet(
                    **sponsee, remaining_owner_count_delta=-3
                ),
                "max_fee alone": lambda: SponsorshipSet(**sponsee, max_fee="100"),
                # Only `fee_amount_delta` is required to be non-zero; `max_fee`
                # is an absolute cap and zero is a meaningful value.
                "max_fee of zero": lambda: SponsorshipSet(**sponsee, max_fee="0"),
                "everything at once": lambda: SponsorshipSet(
                    **sponsee,
                    fee_amount_delta="1000000",
                    max_fee="2000000",
                    remaining_owner_count_delta=5,
                ),
                "flag alone": lambda: SponsorshipSet(
                    **sponsee,
                    flags=SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE,
                ),
                "set fee + set reserve": lambda: SponsorshipSet(
                    **sponsee,
                    flags=(
                        SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_FEE
                        | SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE
                    ),
                ),
                # Only the set/clear pair for the *same* budget conflicts.
                "clear fee + set reserve": lambda: SponsorshipSet(
                    **sponsee,
                    flags=(
                        SponsorshipSetFlag.TF_SPONSORSHIP_CLEAR_REQUIRE_SIGN_FOR_FEE
                        | SponsorshipSetFlag.TF_SPONSORSHIP_SET_REQUIRE_SIGN_FOR_RESERVE
                    ),
                ),
                "delete as the sponsor": lambda: SponsorshipSet(
                    **sponsee, flags=SponsorshipSetFlag.TF_DELETE_OBJECT
                ),
                "delete as the sponsee": lambda: SponsorshipSet(
                    account=_ACCOUNT,
                    counterparty_sponsor=_SPONSEE,
                    flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
                ),
            }
        )

    def test_sponsorship_transfer(self):
        """All three operations, object-level and account-level."""
        incoming = {"sponsor": _SPONSOR, "sponsor_flags": _RESERVE}
        self._accepts(
            {
                "end, bare": lambda: SponsorshipTransfer(
                    account=_ACCOUNT,
                    flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
                ),
                "end, object-level": lambda: SponsorshipTransfer(
                    account=_ACCOUNT,
                    object_id=_OBJECT_ID,
                    flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
                ),
                "end, on behalf of a sponsee": lambda: SponsorshipTransfer(
                    account=_ACCOUNT,
                    sponsee=_SPONSEE,
                    flags=SponsorshipTransferFlag.TF_SPONSORSHIP_END,
                ),
                "create, object-level": lambda: SponsorshipTransfer(
                    account=_ACCOUNT,
                    object_id=_OBJECT_ID,
                    **incoming,
                    flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
                ),
                # No object_id means the account's own reserve.
                "create, account-level": lambda: SponsorshipTransfer(
                    account=_ACCOUNT,
                    **incoming,
                    flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
                ),
                # Reserve is required; fee may ride along.
                "create, fee + reserve": lambda: SponsorshipTransfer(
                    account=_ACCOUNT,
                    object_id=_OBJECT_ID,
                    sponsor=_SPONSOR,
                    sponsor_flags=_FEE | _RESERVE,
                    flags=SponsorshipTransferFlag.TF_SPONSORSHIP_CREATE,
                ),
                "reassign": lambda: SponsorshipTransfer(
                    account=_ACCOUNT,
                    object_id=_OBJECT_ID,
                    **incoming,
                    flags=SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
                ),
            }
        )

    def test_batch_sponsorship(self):
        """Both inner authorization paths, plus a fee-sponsored outer Batch."""
        other = _inner_payment(_SPONSOR)
        self._accepts(
            {
                # Co-signed: the placeholder marks the sponsor as a required
                # BatchSigner.
                "inner reserve, co-signed": lambda: _batch(
                    _inner_payment(
                        _SPONSEE,
                        sponsor=_SPONSOR,
                        sponsor_flags=_RESERVE,
                        sponsor_signature=SponsorSignature(),
                    ),
                    other,
                ),
                # Pre-funded: no placeholder, authorization comes from a
                # Sponsorship object instead.
                "inner reserve, pre-funded": lambda: _batch(
                    _inner_payment(_SPONSEE, sponsor=_SPONSOR, sponsor_flags=_RESERVE),
                    other,
                ),
                # Reserve is barred on the outer Batch; fee is not.
                "outer fee-sponsored": lambda: _batch(
                    _inner_payment(_SPONSEE),
                    other,
                    sponsor=_SPONSOR,
                    sponsor_flags=_FEE,
                ),
            }
        )
