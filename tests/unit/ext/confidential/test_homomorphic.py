"""
Test suite for homomorphic ElGamal ciphertext operations.

Mirrors the Rust ``homomorphic.rs`` roundtrip test: proves that
``Enc(a) + Enc(b)`` decrypts to ``a + b`` and ``Enc(a) - Enc(b)`` decrypts to
``a - b`` under the same key. The subtract case is the ``new CB_S = CB_S -
SenderEncryptedAmount`` update rule rippled applies on a confidential send, which
lets a client chain proofs across a Batch.
"""

import unittest

from xrpl.ext.confidential.crypto_bindings import MPT_CRYPTO_AVAILABLE
from xrpl.ext.confidential.encryption import decrypt, encrypt
from xrpl.ext.confidential.homomorphic import add_ciphertexts, subtract_ciphertexts
from xrpl.ext.confidential.keypair import generate_keypair


def setUpModule() -> None:
    """Skip the module unless the native mpt-crypto extension is built."""
    if not MPT_CRYPTO_AVAILABLE:
        raise unittest.SkipTest("mpt-crypto C extension not built")


class TestHomomorphic(unittest.TestCase):
    """Homomorphic add/subtract on same-key ElGamal ciphertexts."""

    def test_add_and_subtract_roundtrip(self) -> None:
        """Enc(70) + Enc(30) -> 100; Enc(70) - Enc(30) -> 40."""
        privkey, pubkey = generate_keypair()
        a_c1, a_c2, _ = encrypt(pubkey, 70)
        b_c1, b_c2, _ = encrypt(pubkey, 30)

        sum_c1, sum_c2 = add_ciphertexts(a_c1, a_c2, b_c1, b_c2)
        self.assertEqual(decrypt(privkey, sum_c1, sum_c2), 100)

        diff_c1, diff_c2 = subtract_ciphertexts(a_c1, a_c2, b_c1, b_c2)
        self.assertEqual(decrypt(privkey, diff_c1, diff_c2), 40)

    def test_outputs_are_66_char_hex(self) -> None:
        """Both output points are 66-char (33-byte) compressed hex strings."""
        _, pubkey = generate_keypair()
        a_c1, a_c2, _ = encrypt(pubkey, 5)
        b_c1, b_c2, _ = encrypt(pubkey, 3)

        for c1, c2 in (
            add_ciphertexts(a_c1, a_c2, b_c1, b_c2),
            subtract_ciphertexts(a_c1, a_c2, b_c1, b_c2),
        ):
            self.assertEqual(len(c1), 66)
            self.assertEqual(len(c2), 66)
            # Round-trips through bytes.fromhex without error.
            self.assertEqual(len(bytes.fromhex(c1)), 33)
            self.assertEqual(len(bytes.fromhex(c2)), 33)

    def test_rejects_malformed_point(self) -> None:
        """A wrong-length point hex is rejected before touching the library."""
        _, pubkey = generate_keypair()
        a_c1, a_c2, _ = encrypt(pubkey, 1)
        with self.assertRaises(ValueError):
            add_ciphertexts("00", a_c2, a_c1, a_c2)


if __name__ == "__main__":
    unittest.main()
