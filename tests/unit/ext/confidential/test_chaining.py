"""
Unit tests for the confidential-send batch-chaining primitive.

``predict_confidential_send_state`` mirrors rippled's ``chainAfterSend``: the
sender's ConfidentialBalanceSpending is homomorphically decremented by each
send's SenderEncryptedAmount and the version bumps by one. These tests prove the
prediction matches what a decrypt of the resulting ciphertext yields, so a Batch
of chained sends binds each proof to the correct successor state.
"""

import unittest

from xrpl.ext.confidential.crypto_bindings import MPT_CRYPTO_AVAILABLE
from xrpl.ext.confidential.encryption import decrypt, encrypt
from xrpl.ext.confidential.keypair import generate_keypair
from xrpl.ext.confidential.transaction_builders import predict_confidential_send_state


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

        next_version, next_hex = predict_confidential_send_state(
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
            version, balance_hex = predict_confidential_send_state(
                version, balance_hex, s_c1 + s_c2
            )
            self.assertEqual(version, expected_version)
            self.assertEqual(
                decrypt(privkey, balance_hex[:66], balance_hex[66:132], 0, 1000),
                expected_remaining,
            )


if __name__ == "__main__":
    unittest.main()
