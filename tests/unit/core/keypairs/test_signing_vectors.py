from unittest import TestCase

from xrpl.constants import CryptoAlgorithm
from xrpl.core import keypairs

_MESSAGE = b"This test message should verify."

_ED25519 = {
    "seed": "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r",
    "public_key": "ED01FA53FA5A7E77798F882ECE20B1ABC00BB358A9E55A202D0D0676BD0CE37A63",
    "classic_address": "rLUEXYuLiQptky37CqLcm9USQpPiz5rkpD",
    "signature": (
        "5B11F422FB30F0ADB0A598E5410A8B4C008591B660618A01"
        "159BF44B114C73464120A5698D5DA4D95C365F6589D0DB4C"
        "D54CF4323389AEBF9DBC70526218DA08"
    ),
    "unrelated_public_key": (
        "ED6BBFC23A490D021B87D25563C15DA953A7F0F1A493DAA3767FB27F82E2F80C3D"
    ),
}

_SECP256K1 = {
    "seed": "sp5fghtJtpUorTwvof1NpDXAzNwf5",
    "public_key": "030D58EB48B4420B1F7B9DF55087E0E29FEF0E8468F9A6825B01CA2C361042D435",
    "classic_address": "rU6K7V3Po4snVhBBaU29sesqs2qTQJWDw1",
    "signature": (
        "3045022100AEED2C0636E9DB0C3A7795AAF7AE2BF5CBE9163C2004B4F6"
        "CCE172B3ED7023D202204B39347B3AA2A1CD6F38D8E06B2C68C85A826D"
        "695A9D7EF9BDFEEA97FAECB073"
    ),
    "unrelated_public_key": (
        "03B462771E99AAE9C7912AF47D6120C0B0DA972A4043A17F26320A52056DA46EA8"
    ),
}


def _is_rejected(message, signature, public_key):
    try:
        return not keypairs.is_valid_message(message, signature, public_key)
    except Exception:
        return True


class TestSigningVectors(TestCase):
    def test_known_answer_sign_ed25519(self):
        _, private_key = keypairs.derive_keypair(_ED25519["seed"])
        self.assertEqual(keypairs.sign(_MESSAGE, private_key), _ED25519["signature"])

    def test_known_answer_sign_secp256k1(self):
        _, private_key = keypairs.derive_keypair(_SECP256K1["seed"])
        self.assertEqual(keypairs.sign(_MESSAGE, private_key), _SECP256K1["signature"])

    def test_known_answer_verify_ed25519(self):
        self.assertTrue(
            keypairs.is_valid_message(
                _MESSAGE,
                bytes.fromhex(_ED25519["signature"]),
                _ED25519["public_key"],
            )
        )

    def test_known_answer_verify_secp256k1(self):
        self.assertTrue(
            keypairs.is_valid_message(
                _MESSAGE,
                bytes.fromhex(_SECP256K1["signature"]),
                _SECP256K1["public_key"],
            )
        )

    def test_verify_rejects_tampered_message_ed25519(self):
        self.assertFalse(
            keypairs.is_valid_message(
                _MESSAGE + b"!",
                bytes.fromhex(_ED25519["signature"]),
                _ED25519["public_key"],
            )
        )

    def test_verify_rejects_tampered_message_secp256k1(self):
        self.assertFalse(
            keypairs.is_valid_message(
                _MESSAGE + b"!",
                bytes.fromhex(_SECP256K1["signature"]),
                _SECP256K1["public_key"],
            )
        )

    def test_verify_rejects_wrong_public_key_ed25519(self):
        self.assertFalse(
            keypairs.is_valid_message(
                _MESSAGE,
                bytes.fromhex(_ED25519["signature"]),
                _ED25519["unrelated_public_key"],
            )
        )

    def test_verify_rejects_wrong_public_key_secp256k1(self):
        self.assertFalse(
            keypairs.is_valid_message(
                _MESSAGE,
                bytes.fromhex(_SECP256K1["signature"]),
                _SECP256K1["unrelated_public_key"],
            )
        )

    def test_verify_rejects_malformed_signature_ed25519(self):
        signature = bytes.fromhex(_ED25519["signature"])
        public_key = _ED25519["public_key"]
        self.assertTrue(_is_rejected(_MESSAGE, signature[:-1], public_key))
        self.assertTrue(_is_rejected(_MESSAGE, signature + b"\x00", public_key))
        self.assertTrue(_is_rejected(_MESSAGE, b"", public_key))

    def test_verify_rejects_malformed_signature_secp256k1(self):
        signature = bytes.fromhex(_SECP256K1["signature"])
        public_key = _SECP256K1["public_key"]
        self.assertTrue(_is_rejected(_MESSAGE, signature[:-1], public_key))
        self.assertTrue(_is_rejected(_MESSAGE, signature + b"\x00", public_key))
        self.assertTrue(_is_rejected(_MESSAGE, b"", public_key))

    def test_round_trip_ed25519(self):
        self._assert_round_trip(CryptoAlgorithm.ED25519)

    def test_round_trip_secp256k1(self):
        self._assert_round_trip(CryptoAlgorithm.SECP256K1)

    def _assert_round_trip(self, algorithm):
        seed = keypairs.generate_seed(algorithm=algorithm)
        public_key, private_key = keypairs.derive_keypair(seed)
        classic_address = keypairs.derive_classic_address(public_key)
        self.assertTrue(classic_address.startswith("r"))
        signature = keypairs.sign(_MESSAGE, private_key)
        self.assertTrue(
            keypairs.is_valid_message(_MESSAGE, bytes.fromhex(signature), public_key)
        )
        self.assertFalse(
            keypairs.is_valid_message(
                _MESSAGE + b"!", bytes.fromhex(signature), public_key
            )
        )
