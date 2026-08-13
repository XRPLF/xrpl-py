"""
Unit tests for the confidential-send batch-chaining primitive.

``predict_confidential_debit_state`` mirrors rippled's ``chainAfterSend``: the
sender's ConfidentialBalanceSpending is homomorphically decremented by each
send's SenderEncryptedAmount and the version bumps by one. These tests prove the
prediction matches what a decrypt of the resulting ciphertext yields, so a Batch
of chained sends binds each proof to the correct successor state.
"""

import unittest

from xrpl.ext.confidential.crypto_bindings import MPT_CRYPTO_AVAILABLE
from xrpl.ext.confidential.encryption import decrypt, encrypt
from xrpl.ext.confidential.keypair import generate_keypair
from xrpl.ext.confidential.transaction_builders import (
    ConfidentialConvertBackOp,
    ConfidentialMergeInboxOp,
    ConfidentialSendOp,
    _assemble_batch_chain,
    predict_confidential_debit_state,
    predict_confidential_merge_state,
)


def setUpModule() -> None:
    """Skip the module unless the native mpt-crypto extension is built."""
    if not MPT_CRYPTO_AVAILABLE:
        raise unittest.SkipTest("mpt-crypto C extension not built")


class TestPredictConfidentialSendState(unittest.TestCase):
    """The per-send CB_S/version prediction used to chain a Batch of sends."""

    def test_single_step_matches_decrypt(self) -> None:
        """Enc(100) minus a send of 30 predicts Enc(70) at version+1."""
        privkey, pubkey = generate_keypair()
        b_c1, b_c2, _ = encrypt(pubkey, 100)
        s_c1, s_c2, _ = encrypt(pubkey, 30)

        next_version, next_hex = predict_confidential_debit_state(
            5, b_c1 + b_c2, s_c1 + s_c2
        )

        self.assertEqual(next_version, 6)
        self.assertEqual(decrypt(privkey, next_hex[:66], next_hex[66:132], 0, 1000), 70)

    def test_multi_step_chain(self) -> None:
        """Chaining two sends (30, then 25) off Enc(100) predicts Enc(45)."""
        privkey, pubkey = generate_keypair()
        b_c1, b_c2, _ = encrypt(pubkey, 100)
        balance_hex = b_c1 + b_c2
        version = 0

        for amount, expected_remaining, expected_version in ((30, 70, 1), (25, 45, 2)):
            s_c1, s_c2, _ = encrypt(pubkey, amount)
            version, balance_hex = predict_confidential_debit_state(
                version, balance_hex, s_c1 + s_c2
            )
            self.assertEqual(version, expected_version)
            self.assertEqual(
                decrypt(privkey, balance_hex[:66], balance_hex[66:132], 0, 1000),
                expected_remaining,
            )


class TestPredictConfidentialMergeState(unittest.TestCase):
    """The MergeInbox CB_S/version prediction (CB_S + inbox) used to chain."""

    def test_merge_then_debit(self) -> None:
        """Enc(40) spending + Enc(60) inbox merges to Enc(100) at version+1."""
        privkey, pubkey = generate_keypair()
        s_c1, s_c2, _ = encrypt(pubkey, 40)
        i_c1, i_c2, _ = encrypt(pubkey, 60)

        next_version, merged_hex = predict_confidential_merge_state(
            2, s_c1 + s_c2, i_c1 + i_c2
        )
        self.assertEqual(next_version, 3)
        self.assertEqual(
            decrypt(privkey, merged_hex[:66], merged_hex[66:132], 0, 1000), 100
        )

        # A send of 30 chained after the merge leaves 70.
        d_c1, d_c2, _ = encrypt(pubkey, 30)
        version, spend_hex = predict_confidential_debit_state(
            next_version, merged_hex, d_c1 + d_c2
        )
        self.assertEqual(version, 4)
        self.assertEqual(
            decrypt(privkey, spend_hex[:66], spend_hex[66:132], 0, 1000), 70
        )


class TestBatchChainGuards(unittest.TestCase):
    """Fail-fast guards in the builder (which would otherwise tec on-ledger)."""

    _DUMMY_CT = "AB" * 66  # a 132-hex placeholder ciphertext (never decoded here)

    def _chain(self, ops, balance_hex, inbox_hex):
        return _assemble_batch_chain(
            "rAccount",
            "00" * 24,
            ops,
            1,  # first_inner_sequence
            0,  # version
            balance_hex,
            inbox_hex,
            1000,  # range_high
            "priv",
            "pub",
            "issuer",
            None,  # auditor
        )

    def test_merge_on_empty_spending_balance_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "no confidential spending"):
            self._chain([ConfidentialMergeInboxOp()], "", self._DUMMY_CT)

    def test_merge_on_empty_inbox_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "no inbox balance"):
            self._chain([ConfidentialMergeInboxOp()], self._DUMMY_CT, "")

    def test_unrecognized_operation_raises(self) -> None:
        with self.assertRaises(TypeError):
            self._chain([object()], self._DUMMY_CT, self._DUMMY_CT)


class TestConfidentialOpValidation(unittest.TestCase):
    """Op dataclasses reject swapped/invalid inputs at construction."""

    def test_send_op_rejects_short_pubkey(self) -> None:
        # A swapped (address, pubkey) puts a short address where the 66-hex
        # pubkey belongs.
        with self.assertRaisesRegex(ValueError, "receiver_pubkey"):
            ConfidentialSendOp("AB" * 33, "rReceiverAddress", 10)

    def test_send_op_rejects_nonpositive_amount(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            ConfidentialSendOp("rReceiver", "AB" * 33, 0)

    def test_convert_back_op_rejects_nonpositive_amount(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            ConfidentialConvertBackOp(-5)


if __name__ == "__main__":
    unittest.main()
