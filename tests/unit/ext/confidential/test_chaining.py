"""
Unit tests for the confidential-batch state machine.

The predictors mirror rippled: a debit (Send/ConvertBack) homomorphically
decrements the spender's ConfidentialBalanceSpending + mirrors and bumps the
version; a MergeInbox folds the inbox into spending; a Convert credits the
holder's inbox + mirrors; a Clawback resets them. These tests thread real
encrypted balances through the multi-account / multi-token machine and DECRYPT
the predicted states to prove each proof binds to the state the ledger will
leave — so a Batch of chained ops verifies on-ledger.
"""

import unittest

from xrpl.core.addresscodec import decode_classic_address
from xrpl.ext.confidential.crypto_bindings import MPT_CRYPTO_AVAILABLE
from xrpl.ext.confidential.encryption import decrypt, encrypt
from xrpl.ext.confidential.keypair import generate_keypair
from xrpl.ext.confidential.transaction_builders import (
    ConfidentialClawbackOp,
    ConfidentialConvertBackOp,
    ConfidentialConvertOp,
    ConfidentialMergeInboxOp,
    ConfidentialSendOp,
    _assemble_multi_account_batch,
    _TokenState,
    predict_confidential_debit_state,
    predict_confidential_merge_state,
)
from xrpl.wallet import Wallet


def _token_issued_by(issuer_address: str) -> str:
    """A 24-byte MPTokenIssuanceID (hex) whose embedded issuer is ``issuer``.

    The issuer AccountID occupies hex chars 8..48; the Clawback model requires
    ``account == issuer``, so a clawback test must use a token the issuer issues.
    """
    return "00000001" + decode_classic_address(issuer_address).hex().upper()


def setUpModule() -> None:
    """Skip the module unless the native mpt-crypto extension is built."""
    if not MPT_CRYPTO_AVAILABLE:
        raise unittest.SkipTest("mpt-crypto C extension not built")


_TOKEN = "00" * 24
_TOKEN_B = "11" * 24


def _ct(pubkey: str, amount: int) -> str:
    """A 132-hex ElGamal ciphertext of ``amount`` under ``pubkey``."""
    c1, c2, _ = encrypt(pubkey, amount)
    return c1 + c2


def _dec(privkey: str, balance_hex: str) -> int:
    return decrypt(privkey, balance_hex[:66], balance_hex[66:132], 0, 100000)


class TestPredictConfidentialSendState(unittest.TestCase):
    """The per-debit CB_S/version prediction used to chain a Batch."""

    def test_single_step_matches_decrypt(self) -> None:
        """Enc(100) minus a send of 30 predicts Enc(70) at version+1."""
        privkey, pubkey = generate_keypair()
        next_version, next_hex = predict_confidential_debit_state(
            5, _ct(pubkey, 100), _ct(pubkey, 30)
        )
        self.assertEqual(next_version, 6)
        self.assertEqual(_dec(privkey, next_hex), 70)

    def test_multi_step_chain(self) -> None:
        """Chaining two sends (30, then 25) off Enc(100) predicts Enc(45)."""
        privkey, pubkey = generate_keypair()
        balance_hex = _ct(pubkey, 100)
        version = 0
        for amount, expected_remaining, expected_version in ((30, 70, 1), (25, 45, 2)):
            version, balance_hex = predict_confidential_debit_state(
                version, balance_hex, _ct(pubkey, amount)
            )
            self.assertEqual(version, expected_version)
            self.assertEqual(_dec(privkey, balance_hex), expected_remaining)


class TestPredictConfidentialMergeState(unittest.TestCase):
    """The MergeInbox CB_S/version prediction (CB_S + inbox)."""

    def test_merge_then_debit(self) -> None:
        """Enc(40) spending + Enc(60) inbox merges to Enc(100) at version+1."""
        privkey, pubkey = generate_keypair()
        next_version, merged_hex = predict_confidential_merge_state(
            2, _ct(pubkey, 40), _ct(pubkey, 60)
        )
        self.assertEqual(next_version, 3)
        self.assertEqual(_dec(privkey, merged_hex), 100)

        version, spend_hex = predict_confidential_debit_state(
            next_version, merged_hex, _ct(pubkey, 30)
        )
        self.assertEqual(version, 4)
        self.assertEqual(_dec(privkey, spend_hex), 70)


class TestConfidentialOpValidation(unittest.TestCase):
    """Op dataclasses reject swapped/invalid inputs at construction."""

    def test_send_op_rejects_short_pubkey(self) -> None:
        # A swapped (address, pubkey) puts a short address where the 66-hex
        # pubkey belongs.
        with self.assertRaisesRegex(ValueError, "receiver_pubkey"):
            ConfidentialSendOp(
                "rSender",
                _TOKEN,
                "rReceiver",
                "rReceiverAddress",
                10,
                "ab" * 32,
                "AB" * 33,
                "CD" * 33,
            )

    def test_send_op_rejects_nonpositive_amount(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            ConfidentialSendOp(
                "rSender",
                _TOKEN,
                "rReceiver",
                "AB" * 33,
                0,
                "ab" * 32,
                "AB" * 33,
                "CD" * 33,
            )

    def test_convert_back_op_rejects_nonpositive_amount(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            ConfidentialConvertBackOp(
                "rAcct", _TOKEN, -5, "ab" * 32, "AB" * 33, "CD" * 33
            )

    def test_convert_op_allows_zero_amount(self) -> None:
        # Zero is valid for Convert (the key-registration path).
        op = ConfidentialConvertOp("rAcct", _TOKEN, 0, "ab" * 32, "AB" * 33, "CD" * 33)
        self.assertEqual(op.amount, 0)

    def test_clawback_op_rejects_nonpositive_amount(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            ConfidentialClawbackOp(
                "rIssuer", _TOKEN, "rHolder", 0, "ab" * 32, "AB" * 33
            )


class TestMultiAccountBatch(unittest.TestCase):
    """End-to-end (pure) runs of the multi-account/multi-token state machine.

    Real proofs are generated; the predicted post-batch states are decrypted to
    confirm each proof bound to the state the ledger will actually leave.
    """

    def setUp(self) -> None:
        self.issuer_sk, self.issuer_pk = generate_keypair()
        self.a_sk, self.a_pk = generate_keypair()
        self.b_sk, self.b_pk = generate_keypair()
        # Context-hash construction decodes the account/destination/holder as
        # classic addresses, so use real (valid-checksum) ones.
        self.a = Wallet.create().address
        self.b = Wallet.create().address
        self.c = Wallet.create().address
        self.issuer = Wallet.create().address

    def _funded_holder(self, pubkey: str, spending: int) -> _TokenState:
        return _TokenState(
            spending=_ct(pubkey, spending),
            inbox=_ct(pubkey, 0),
            issuer_enc=_ct(self.issuer_pk, spending),
            auditor_enc=None,
            version=0,
            holder_key=pubkey,
        )

    def _run(self, ops, states):
        next_seq = {op.account: 10 for op in ops}
        range_highs = {op.mpt_issuance_id: 100000 for op in ops}
        return _assemble_multi_account_batch(list(ops), states, next_seq, range_highs)

    def test_multi_account_cross_send(self) -> None:
        # A -> B (30) and B -> A (25) in one batch. Verify both spenders'
        # predicted balances and both recipients' inboxes decrypt correctly.
        states = {
            (self.a, _TOKEN): self._funded_holder(self.a_pk, 1000),
            (self.b, _TOKEN): self._funded_holder(self.b_pk, 500),
        }
        ops = [
            ConfidentialSendOp(
                self.a,
                _TOKEN,
                self.b,
                self.b_pk,
                30,
                self.a_sk,
                self.a_pk,
                self.issuer_pk,
            ),
            ConfidentialSendOp(
                self.b,
                _TOKEN,
                self.a,
                self.a_pk,
                25,
                self.b_sk,
                self.b_pk,
                self.issuer_pk,
            ),
        ]
        txs = self._run(ops, states)
        self.assertEqual(len(txs), 2)
        # Sequences pinned per-account starting at 10.
        self.assertEqual(txs[0].sequence, 10)
        self.assertEqual(txs[1].sequence, 10)

        self.assertEqual(_dec(self.a_sk, states[(self.a, _TOKEN)].spending), 970)
        self.assertEqual(_dec(self.b_sk, states[(self.b, _TOKEN)].spending), 475)
        # Recipients' predicted inboxes: A received 25, B received 30.
        self.assertEqual(_dec(self.a_sk, states[(self.a, _TOKEN)].inbox), 25)
        self.assertEqual(_dec(self.b_sk, states[(self.b, _TOKEN)].inbox), 30)
        # Issuer mirror tracks each holder's TOTAL holding (spending + inbox), so
        # it reflects both the send debit AND the receive credit:
        # A: 1000 - 30 + 25 = 995; B: 500 - 25 + 30 = 505.
        self.assertEqual(_dec(self.issuer_sk, states[(self.a, _TOKEN)].issuer_enc), 995)
        self.assertEqual(_dec(self.issuer_sk, states[(self.b, _TOKEN)].issuer_enc), 505)

    def test_multi_token_independent_chains(self) -> None:
        # Same account A spends on two different tokens; chains are independent.
        states = {
            (self.a, _TOKEN): self._funded_holder(self.a_pk, 1000),
            (self.a, _TOKEN_B): self._funded_holder(self.a_pk, 800),
            (self.b, _TOKEN): self._funded_holder(self.b_pk, 0),
            (self.b, _TOKEN_B): self._funded_holder(self.b_pk, 0),
        }
        ops = [
            ConfidentialSendOp(
                self.a,
                _TOKEN,
                self.b,
                self.b_pk,
                100,
                self.a_sk,
                self.a_pk,
                self.issuer_pk,
            ),
            ConfidentialSendOp(
                self.a,
                _TOKEN_B,
                self.b,
                self.b_pk,
                50,
                self.a_sk,
                self.a_pk,
                self.issuer_pk,
            ),
        ]
        self._run(ops, states)
        self.assertEqual(_dec(self.a_sk, states[(self.a, _TOKEN)].spending), 900)
        self.assertEqual(_dec(self.a_sk, states[(self.a, _TOKEN_B)].spending), 750)

    def test_send_credits_destination_issuer_mirror(self) -> None:
        # THE FIX: on a Send, the destination's IssuerEncryptedBalance is credited
        # too (xrpl.js advanced only the inbox). Run the send alone and confirm
        # B's predicted mirror rose from 100 to 140 — the value a same-batch
        # Clawback of B must bind to.
        send = ConfidentialSendOp(
            self.a, _TOKEN, self.b, self.b_pk, 40, self.a_sk, self.a_pk, self.issuer_pk
        )
        states = {
            (self.a, _TOKEN): self._funded_holder(self.a_pk, 1000),
            (self.b, _TOKEN): self._funded_holder(self.b_pk, 100),
        }
        self._run([send], states)
        self.assertEqual(_dec(self.issuer_sk, states[(self.b, _TOKEN)].issuer_enc), 140)
        self.assertEqual(_dec(self.b_sk, states[(self.b, _TOKEN)].inbox), 40)

    def test_clawback_after_send_binds_post_send_mirror(self) -> None:
        # Send A -> B (40), then issuer claws back B (140) in the SAME batch. The
        # clawback proof proves B's IssuerEncryptedBalance decrypts to 140; the
        # send credited that mirror, so building the proof against the predicted
        # post-send mirror succeeds. If the mirror were left stale (100), the
        # amount-140 proof would fail to generate — so a clean build proves the
        # fix. Clawback requires account == issuer, so use a token self.issuer
        # actually issues.
        token = _token_issued_by(self.issuer)
        states = {
            (self.a, token): self._funded_holder(self.a_pk, 1000),
            (self.b, token): self._funded_holder(self.b_pk, 100),
        }
        ops = [
            ConfidentialSendOp(
                self.a,
                token,
                self.b,
                self.b_pk,
                40,
                self.a_sk,
                self.a_pk,
                self.issuer_pk,
            ),
            ConfidentialClawbackOp(
                self.issuer, token, self.b, 140, self.issuer_sk, self.issuer_pk
            ),
        ]
        txs = self._run(ops, states)
        self.assertEqual(len(txs), 2)
        self.assertEqual(txs[1].mpt_amount, 140)
        # Clawback reset B's predicted balances (version bumped).
        self.assertIsNone(states[(self.b, token)].spending)
        self.assertEqual(states[(self.b, token)].version, 1)

    def test_convert_then_send_registers_key_once(self) -> None:
        # A brand-new holder C: Convert (registers key, credits inbox), then A
        # sends to C. The Convert's predicted holder key lets the send encrypt to
        # C, and a first-ever convert initializes C's inbox.
        c_sk, c_pk = generate_keypair()
        states = {
            (self.a, _TOKEN): self._funded_holder(self.a_pk, 1000),
            # C not yet on-ledger: empty state.
            (self.c, _TOKEN): _TokenState(),
        }
        ops = [
            ConfidentialConvertOp(self.c, _TOKEN, 200, c_sk, c_pk, self.issuer_pk),
            ConfidentialSendOp(
                self.a, _TOKEN, self.c, c_pk, 30, self.a_sk, self.a_pk, self.issuer_pk
            ),
        ]
        txs = self._run(ops, states)
        # The Convert registered the key (holder_encryption_key present).
        self.assertIsNotNone(txs[0].holder_encryption_key)
        # C's predicted state now carries the registered key and a 230 inbox.
        self.assertEqual(states[(self.c, _TOKEN)].holder_key, c_pk)
        self.assertEqual(_dec(c_sk, states[(self.c, _TOKEN)].inbox), 230)

    def test_merge_then_send_chains(self) -> None:
        # A has spending 40 and inbox 60; MergeInbox folds to 100, then a send of
        # 25 leaves 75. Both inners are A's, sequences 10 and 11.
        states = {
            (self.a, _TOKEN): _TokenState(
                spending=_ct(self.a_pk, 40),
                inbox=_ct(self.a_pk, 60),
                issuer_enc=_ct(self.issuer_pk, 40),
                version=3,
                holder_key=self.a_pk,
            ),
            (self.b, _TOKEN): self._funded_holder(self.b_pk, 0),
        }
        ops = [
            ConfidentialMergeInboxOp(self.a, _TOKEN),
            ConfidentialSendOp(
                self.a,
                _TOKEN,
                self.b,
                self.b_pk,
                25,
                self.a_sk,
                self.a_pk,
                self.issuer_pk,
            ),
        ]
        txs = self._run(ops, states)
        self.assertEqual(txs[0].sequence, 10)
        self.assertEqual(txs[1].sequence, 11)
        self.assertEqual(_dec(self.a_sk, states[(self.a, _TOKEN)].spending), 75)
        # Version bumped by both the merge and the send.
        self.assertEqual(states[(self.a, _TOKEN)].version, 5)

    def test_second_merge_on_consumed_inbox_raises(self) -> None:
        states = {
            (self.a, _TOKEN): _TokenState(
                spending=_ct(self.a_pk, 40),
                inbox=_ct(self.a_pk, 60),
                issuer_enc=_ct(self.issuer_pk, 40),
                version=0,
                holder_key=self.a_pk,
            ),
        }
        ops = [
            ConfidentialMergeInboxOp(self.a, _TOKEN),
            ConfidentialMergeInboxOp(self.a, _TOKEN),
        ]
        with self.assertRaisesRegex(ValueError, "no inbox balance"):
            self._run(ops, states)

    def test_unrecognized_operation_raises(self) -> None:
        from types import SimpleNamespace

        bogus = SimpleNamespace(account="rX", mpt_issuance_id=_TOKEN)
        with self.assertRaises(TypeError):
            _assemble_multi_account_batch([bogus], {}, {"rX": 10}, {_TOKEN: 100000})


if __name__ == "__main__":
    unittest.main()
