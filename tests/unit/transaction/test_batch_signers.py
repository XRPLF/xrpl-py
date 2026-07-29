from unittest import TestCase

from xrpl.constants import CryptoAlgorithm, XRPLException
from xrpl.core.addresscodec.codec import decode_classic_address
from xrpl.core.binarycodec.main import decode
from xrpl.models.transactions import Batch, BatchFlag, Signer
from xrpl.models.transactions.batch import BatchSigner
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import sign
from xrpl.transaction.batch_signers import (
    combine_batch_signers,
    sign_multiaccount_batch,
)
from xrpl.wallet import Wallet

secp_wallet = Wallet.from_seed(
    "spkcsko6Ag3RbCSVXV2FJ8Pd4Zac1",
    algorithm=CryptoAlgorithm.SECP256K1,
)
ed_wallet = Wallet.from_seed(
    "spkcsko6Ag3RbCSVXV2FJ8Pd4Zac1",
    algorithm=CryptoAlgorithm.ED25519,
)
submit_wallet = Wallet.from_seed(
    "sEd7HmQFsoyj5TAm6d98gytM9LJA1MF",
    algorithm=CryptoAlgorithm.ED25519,
)
regkey_wallet = Wallet.from_seed(
    "sEdStM1pngFcLQqVfH3RQcg2Qr6ov9e",
    algorithm=CryptoAlgorithm.ED25519,
)
other_wallet = Wallet.create()

REGKEY_PUBLIC_KEY = "ED37D3F048B7F1E680B0A97F70C7843160B9F25D6398D07E68B9A2C83AA8E1B156"


class TestSignMultiAccountBatch(TestCase):
    batch_tx = Batch.from_xrpl(
        {
            "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
            "Flags": 1,
            "RawTransactions": [
                {
                    "RawTransaction": {
                        "Account": "rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                        "Flags": 1073741824,
                        "Amount": "5000000",
                        "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Fee": "0",
                        "Sequence": 215,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
                {
                    "RawTransaction": {
                        "Account": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Amount": "1000000",
                        "Flags": 1073741824,
                        "Destination": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                        "Fee": "0",
                        "Sequence": 470,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
            ],
            "TransactionType": "Batch",
        }
    )

    def test_secp_wallet(self):
        result = sign_multiaccount_batch(secp_wallet, self.batch_tx)
        expected = [
            BatchSigner(
                account="rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                signing_pub_key=(
                    "02691AC5AE1C4C333AE5DF8A93BDC495F0EEBFC6DB0DA7EB6EF80"
                    "8F3AFC006E3FE"
                ),
                txn_signature=(
                    "304502210098890858AA57D6515D7C523FE076FA97BFA87DA666A87B4A7CF44249"
                    "181DC1DC02201B90E513FE2F45D41FB31850F463C0ECBA8F5126B1AF431B67C400"
                    "4CA0DD8042"
                ),
            )
        ]

        self.assertIsNotNone(result.batch_signers)
        self.assertEqual(result.batch_signers, expected)

    def test_ed_wallet(self):
        result = sign_multiaccount_batch(ed_wallet, self.batch_tx)
        expected = [
            BatchSigner(
                account="rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                signing_pub_key=(
                    "ED3CC3D14FD80C213BC92A98AFE13A405A030F845EDCFD5E39528"
                    "6A6E9E62BA638"
                ),
                txn_signature=(
                    "27B496F0C1F2C4789A0E6CF25265069980190C786053CF5D6C066C07E21D632A6E"
                    "B87C56275109A8542EEDE782FDC5591EA51FAF28C3FCFCF35BCE960F1D8601"
                ),
            )
        ]

        self.assertIsNotNone(result.batch_signers)
        self.assertEqual(result.batch_signers, expected)

    def test_different_account(self):
        # Sign with a regular key on behalf of an account in the Batch.
        result = sign_multiaccount_batch(
            regkey_wallet, self.batch_tx, batch_account=ed_wallet.address
        )
        expected = [
            BatchSigner(
                account="rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                signing_pub_key=REGKEY_PUBLIC_KEY,
                txn_signature=(
                    "046315C731DF089E08EB6662251F12B22938ED462F66BC561A847A87DF6B3C9AC8"
                    "11D9EC5971EDEC2BA96C959BDE883CD838B7EF6460A47AD9B71518F1A2A00B"
                ),
            )
        ]

        self.assertEqual(result.batch_signers, expected)

    def test_multisign(self):
        result = sign_multiaccount_batch(
            regkey_wallet,
            self.batch_tx,
            multisign=True,
            batch_account=ed_wallet.address,
        )
        expected = [
            BatchSigner(
                account="rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                signers=[
                    Signer(
                        account="rwRNeznwHzdfYeKWpevYmax2NSDioyeEtT",
                        signing_pub_key=REGKEY_PUBLIC_KEY,
                        txn_signature=(
                            "8FCA6C1056C2146DC13F4D10BA297335A82F562D837FA3C65D75DCDC87"
                            "540F61428B7370FCC1DE4D83B6FA1A00A18CD9283E7B08089091ED84CC"
                            "3E4A8B43F00F"
                        ),
                    )
                ],
            )
        ]

        self.assertEqual(result.batch_signers, expected)

    def test_multisign_with_regular_key(self):
        result = sign_multiaccount_batch(
            regkey_wallet,
            self.batch_tx,
            multisign=submit_wallet.address,
            batch_account=ed_wallet.address,
        )
        expected = [
            BatchSigner(
                account="rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                signers=[
                    Signer(
                        account="rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                        signing_pub_key=REGKEY_PUBLIC_KEY,
                        txn_signature=(
                            "D80D4195BF67D5CB12CA225D04DA4D00AC77250803671E09DF61F1695A"
                            "831FAD6BF820F335DD2D8CFE16DA55CFC2E64AEC8A1429524E6CDB6C36"
                            "B7AEA717C700"
                        ),
                    )
                ],
            )
        ]

        self.assertEqual(result.batch_signers, expected)

    def test_not_included_account(self):
        with self.assertRaises(XRPLException):
            sign_multiaccount_batch(other_wallet, self.batch_tx)

    def test_self_multisign_raises(self):
        # multisign=True with no batch_account makes the signer sign for itself.
        with self.assertRaises(XRPLException):
            sign_multiaccount_batch(secp_wallet, self.batch_tx, multisign=True)

    def test_multisign_signer_equals_batch_account_raises(self):
        with self.assertRaises(XRPLException):
            sign_multiaccount_batch(
                secp_wallet,
                self.batch_tx,
                multisign=ed_wallet.address,
                batch_account=ed_wallet.address,
            )

    # An inner transaction's sponsor authorizes through the outer BatchSigners,
    # never through the inner's SponsorSignature (XLS-68 §13.3). rippled counts
    # the sponsor as a required signer when `Sponsor` and `SponsorSignature` are
    # both present, and rejects the whole Batch with temBAD_SIGNER if
    # BatchSigners does not match its required set exactly.
    sponsored_batch_tx = Batch.from_xrpl(
        {
            "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
            "Flags": 1,
            "RawTransactions": [
                {
                    "RawTransaction": {
                        "Account": "rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                        "Flags": 1073741824,
                        "Amount": "5000000",
                        "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Fee": "0",
                        "Sequence": 215,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                        "Sponsor": other_wallet.address,
                        "SponsorFlags": 2,  # spfSponsorReserve
                        "SponsorSignature": {},  # empty placeholder
                    },
                },
                {
                    "RawTransaction": {
                        "Account": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Amount": "1000000",
                        "Flags": 1073741824,
                        "Destination": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                        "Fee": "0",
                        "Sequence": 470,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
            ],
            "TransactionType": "Batch",
        }
    )

    def test_inner_transaction_sponsor_may_sign(self):
        signed = sign_multiaccount_batch(other_wallet, self.sponsored_batch_tx)
        self.assertEqual(len(signed.batch_signers), 1)
        self.assertEqual(signed.batch_signers[0].account, other_wallet.address)

    def test_inner_sponsor_without_placeholder_may_not_sign(self):
        # No SponsorSignature -> rippled does not require the sponsor's entry, so
        # an extra BatchSigner would be rejected as "extra signer provided".
        with self.assertRaises(XRPLException):
            sign_multiaccount_batch(other_wallet, self.batch_tx)

    def test_sponsored_batch_signers_match_required_set(self):
        # rippled's required set here is {inner-0 authorizer, inner-0 sponsor,
        # inner-1 authorizer}. The outer account signs the Batch itself and must
        # not appear in BatchSigners.
        parts = [
            sign_multiaccount_batch(ed_wallet, self.sponsored_batch_tx),
            sign_multiaccount_batch(secp_wallet, self.sponsored_batch_tx),
            sign_multiaccount_batch(other_wallet, self.sponsored_batch_tx),
        ]
        merged = Transaction.from_blob(combine_batch_signers(parts))
        accounts = [signer.account for signer in merged.batch_signers]
        self.assertEqual(
            set(accounts),
            {ed_wallet.address, secp_wallet.address, other_wallet.address},
        )
        self.assertNotIn(submit_wallet.address, accounts)
        ids = [decode_classic_address(a).hex() for a in accounts]
        self.assertEqual(ids, sorted(ids))


class TestCombineBatchSigners(TestCase):
    batch_tx = Batch.from_xrpl(
        {
            "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
            "Flags": 1,
            "LastLedgerSequence": 14973,
            "NetworkID": 21336,
            "RawTransactions": [
                {
                    "RawTransaction": {
                        "Account": "rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                        "Amount": "5000000",
                        "Flags": 1073741824,
                        "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
                {
                    "RawTransaction": {
                        "Account": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Amount": "1000000",
                        "Flags": 1073741824,
                        "Destination": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
            ],
            "Sequence": 215,
            "TransactionType": "Batch",
        }
    )
    tx1 = sign_multiaccount_batch(ed_wallet, batch_tx)
    tx2 = sign_multiaccount_batch(secp_wallet, batch_tx)
    expected_valid = tx1.to_xrpl().get("BatchSigners", []) + tx2.to_xrpl().get(
        "BatchSigners", []
    )

    def test_valid(self):
        result = combine_batch_signers([self.tx1, self.tx2])
        self.assertEqual(decode(result)["BatchSigners"], self.expected_valid)

    def test_valid_serialized(self):
        result = combine_batch_signers([self.tx1.blob(), self.tx2.blob()])
        self.assertEqual(decode(result)["BatchSigners"], self.expected_valid)

    def test_valid_sorted(self):
        result = combine_batch_signers([self.tx2, self.tx1])
        self.assertEqual(decode(result)["BatchSigners"], self.expected_valid)

    def test_remove_submitter_signature(self):
        tx = Transaction.from_xrpl(
            {
                "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                "Amount": "1000000",
                "Flags": 1073741824,
                "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                "Fee": "0",
                "NetworkID": 21336,
                "Sequence": 0,
                "SigningPubKey": "",
                "TransactionType": "Payment",
            }
        )
        original_dict = self.batch_tx.to_xrpl()
        original_dict["RawTransactions"].append({"RawTransaction": tx.to_xrpl()})

        batch_tx = Batch.from_xrpl(original_dict)
        tx1 = sign_multiaccount_batch(ed_wallet, batch_tx)
        tx2 = sign_multiaccount_batch(secp_wallet, batch_tx)
        tx3 = sign_multiaccount_batch(submit_wallet, batch_tx)

        result = combine_batch_signers([tx1, tx2, tx3])
        expected_valid = tx1.to_xrpl().get("BatchSigners", []) + tx2.to_xrpl().get(
            "BatchSigners", []
        )
        self.assertEqual(decode(result)["BatchSigners"], expected_valid)

    def test_dedup_shared_signer(self):
        # Combining fragments that share a signer keeps a single, unique signer.
        result = combine_batch_signers([self.tx1, self.tx1])
        self.assertEqual(
            decode(result)["BatchSigners"], self.tx1.to_xrpl()["BatchSigners"]
        )

    def test_no_transactions(self):
        with self.assertRaises(XRPLException):
            combine_batch_signers([])

    def test_signed_batch_rejected(self):
        # A fully signed outer Batch cannot be combined.
        signed_blob = sign(self.tx1, secp_wallet).blob()
        with self.assertRaises(XRPLException):
            combine_batch_signers([signed_blob, self.tx2])

    def _signed_with_field(self, **overrides):
        bad_dict = {**self.batch_tx.to_xrpl(), **overrides}
        return sign_multiaccount_batch(secp_wallet, Batch.from_xrpl(bad_dict))

    def test_different_flags(self):
        bad_tx = self._signed_with_field(Flags=int(BatchFlag.TF_INDEPENDENT))
        with self.assertRaises(XRPLException):
            combine_batch_signers([self.tx1, bad_tx])

    def test_different_account(self):
        bad_tx = self._signed_with_field(Account="rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7")
        with self.assertRaises(XRPLException):
            combine_batch_signers([self.tx1, bad_tx])

    def test_different_sequence(self):
        bad_tx = self._signed_with_field(Sequence=216)
        with self.assertRaises(XRPLException):
            combine_batch_signers([self.tx1, bad_tx])

    def test_merge_multisigned_inner_signers(self):
        # Fragments sharing a multisig batch account merge into one BatchSigner.
        frag1 = sign_multiaccount_batch(
            regkey_wallet,
            self.batch_tx,
            multisign=True,
            batch_account=ed_wallet.address,
        )
        frag2 = sign_multiaccount_batch(
            submit_wallet,
            self.batch_tx,
            multisign=True,
            batch_account=ed_wallet.address,
        )
        result = decode(combine_batch_signers([frag1, frag2]))["BatchSigners"]

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["BatchSigner"]["Account"], ed_wallet.address)
        inner = result[0]["BatchSigner"]["Signers"]
        self.assertEqual(len(inner), 2)
        signer_accounts = [entry["Signer"]["Account"] for entry in inner]
        self.assertEqual(
            set(signer_accounts), {regkey_wallet.address, submit_wallet.address}
        )
        # Inner Signers must be sorted by AccountID bytes.
        expected_order = sorted(
            signer_accounts,
            key=lambda account: decode_classic_address(account).hex().upper(),
        )
        self.assertEqual(signer_accounts, expected_order)

    def test_mismatched_single_and_multi_signed(self):
        # Single-signed and multi-signed fragments for one account cannot combine.
        single = sign_multiaccount_batch(ed_wallet, self.batch_tx)
        multi = sign_multiaccount_batch(
            regkey_wallet,
            self.batch_tx,
            multisign=True,
            batch_account=ed_wallet.address,
        )
        with self.assertRaises(XRPLException):
            combine_batch_signers([single, multi])

    def test_conflicting_inner_signers_raises(self):
        # Same batch account and inner signer account across fragments, but a
        # different signature -- merging must raise, not silently drop one.
        frag1 = sign_multiaccount_batch(
            regkey_wallet,
            self.batch_tx,
            multisign=True,
            batch_account=ed_wallet.address,
        )
        conflicting_dict = self.batch_tx.to_dict()
        conflicting_dict["batch_signers"] = [
            BatchSigner(
                account=ed_wallet.address,
                signers=[
                    Signer(
                        account=regkey_wallet.address,
                        signing_pub_key=regkey_wallet.public_key,
                        txn_signature="DEADBEEF",
                    )
                ],
            )
        ]
        frag2 = Batch.from_dict(conflicting_dict)

        with self.assertRaises(XRPLException):
            combine_batch_signers([frag1, frag2])
