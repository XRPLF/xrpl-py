from unittest import TestCase
from unittest.mock import patch

from xrpl.constants import CryptoAlgorithm
from xrpl.core import keypairs
from xrpl.core.keypairs.exceptions import XRPLKeypairsException

_DUMMY_BYTES = b"\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10"


class TestMain(TestCase):
    # unfortunately, this patching is very brittle; it depends on the syntax
    # used to import secrets within the calling module.
    @patch(
        "xrpl.core.keypairs.main.token_bytes", autospec=True, return_value=_DUMMY_BYTES
    )
    def test_generate_seed_no_params(self, _randbytes):
        output = keypairs.generate_seed()
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_entropy_provided(self):
        output = keypairs.generate_seed(_DUMMY_BYTES.decode("UTF-8"))
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_ed25519(self):
        output = keypairs.generate_seed(
            _DUMMY_BYTES.decode("UTF-8"), CryptoAlgorithm.ED25519
        )
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_secp256k1(self):
        output = keypairs.generate_seed(
            _DUMMY_BYTES.decode("UTF-8"), CryptoAlgorithm.SECP256K1
        )
        self.assertEqual(output, "sp5fghtJtpUorTwvof1NpDXAzNwf5")

    def test_derive_keypair_ed25519(self):
        public, private = keypairs.derive_keypair("sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")
        self.assertEqual(
            public,
            "ED01FA53FA5A7E77798F882ECE20B1ABC00BB358A9E55A202D0D0676BD0CE37A63",
        )
        self.assertEqual(
            private,
            "EDB4C4E046826BD26190D09715FC31F4E6A728204EADD112905B08B14B7F15C4F3",
        )

    def test_derive_keypair_ed25519_validator(self):
        with self.assertRaises(XRPLKeypairsException):
            keypairs.derive_keypair("sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r", validator=True)

    def test_derive_keypair_ed25519_different_prefix(self):
        public, private = keypairs.derive_keypair(
            "ssB9S5Mca2hGZ73xNs4gruS1GY7fB", algorithm=CryptoAlgorithm.ED25519
        )
        self.assertEqual(
            public,
            "ED6BBFC23A490D021B87D25563C15DA953A7F0F1A493DAA3767FB27F82E2F80C3D",
        )
        self.assertEqual(
            private,
            "ED644E705250E4D736875E85DD3E5FBABA4E12E004549202010228E17D3D574576",
        )

    def test_derive_keypair_secp256k1(self):
        public, private = keypairs.derive_keypair("sp5fghtJtpUorTwvof1NpDXAzNwf5")
        self.assertEqual(
            public,
            "030D58EB48B4420B1F7B9DF55087E0E29FEF0E8468F9A6825B01CA2C361042D435",
        )
        self.assertEqual(
            private,
            "00D78B9735C3F26501C7337B8A5727FD53A6EFDBC6AA55984F098488561F985E23",
        )

    def test_derive_keypair_secp256k1_validator(self):
        public, private = keypairs.derive_keypair(
            "sp5fghtJtpUorTwvof1NpDXAzNwf5",
            validator=True,
        )
        self.assertEqual(
            public,
            "03B462771E99AAE9C7912AF47D6120C0B0DA972A4043A17F26320A52056DA46EA8",
        )
        self.assertEqual(
            private,
            "001A6B48BF0DE7C7E425B61E0444E3921182B6529867685257CEDC3E7EF13F0F18",
        )

    def test_derive_classic_address_ed25519(self):
        self.assertEqual(
            keypairs.derive_classic_address(
                "ED01FA53FA5A7E77798F882ECE20B1ABC00BB358A9E55A202D0D0676BD0CE37A63",
            ),
            "rLUEXYuLiQptky37CqLcm9USQpPiz5rkpD",
        )

    def test_derive_classic_address_secp256k1(self):
        self.assertEqual(
            keypairs.derive_classic_address(
                "030D58EB48B4420B1F7B9DF55087E0E29FEF0E8468F9A6825B01CA2C361042D435",
            ),
            "rU6K7V3Po4snVhBBaU29sesqs2qTQJWDw1",
        )

    def test_sign_ed25519(self):
        signature = keypairs.sign(
            b"test message",
            "EDB4C4E046826BD26190D09715FC31F4E6A728204EADD112905B08B14B7F15C4F3",
        )
        self.assertEqual(
            signature,
            (
                "CB199E1BFD4E3DAA105E4832EEDFA36413E1F44205E"
                "4EFB9E27E826044C21E3E2E848BBC8195E8959BADF8"
                "87599B7310AD1B7047EF11B682E0D068F73749750E"
            ),
        )

    def test_sign_secp256k1(self):
        signature = keypairs.sign(
            b"test message",
            "00D78B9735C3F26501C7337B8A5727FD53A6EFDBC6AA55984F098488561F985E23",
        )
        self.assertEqual(
            signature,
            (
                "30440220583A91C95E54E6A651C47BEC22744E0B101"
                "E2C4060E7B08F6341657DAD9BC3EE02207D1489C739"
                "5DB0188D3A56A977ECBA54B36FA9371B40319655B1B4429E33EF2D"
            ),
        )

    def test_is_valid_message_ed25519(self):
        output = keypairs.is_valid_message(
            b"test message",
            bytes.fromhex(
                (
                    "CB199E1BFD4E3DAA105E4832EEDFA36413E1F442"
                    "05E4EFB9E27E826044C21E3E2E848BBC8195E895"
                    "9BADF887599B7310AD1B7047EF11B682E0D068F73749750E"
                ),
            ),
            "ED01FA53FA5A7E77798F882ECE20B1ABC00BB358A9E55A202D0D0676BD0CE37A63",
        )
        self.assertTrue(output)

    def test_is_valid_message_secp256k1(self):
        output = keypairs.is_valid_message(
            b"test message",
            bytes.fromhex(
                (
                    "30440220583A91C95E54E6A651C47BEC22744E0B101E2C"
                    "4060E7B08F6341657DAD9BC3EE02207D1489C7395DB018"
                    "8D3A56A977ECBA54B36FA9371B40319655B1B4429E33EF2D"
                ),
            ),
            "030D58EB48B4420B1F7B9DF55087E0E29FEF0E8468F9A6825B01CA2C361042D435",
        )
        self.assertTrue(output)

    def test_is_valid_message_ed25519_bad_key(self):
        output = keypairs.is_valid_message(
            b"test message",
            bytes.fromhex(
                (
                    "CB199E1BFD4E3DAA105E4832EEDFA36413E1F442"
                    "05E4EFB9E27E826044C21E3E2E848BBC8195E895"
                    "9BADF887599B7310AD1B7047EF11B682E0D068F73749750E"
                ),
            ),
            "ED11FA53FA5A7E77798F882ECE20B1ABC00BB358A9E55A202D0D0676BD0CE37A63",
        )
        self.assertFalse(output)

    def test_is_valid_message_secp256k1_bad_key(self):
        output = keypairs.is_valid_message(
            b"test message",
            bytes.fromhex(
                (
                    "30440220583A91C95E54E6A651C47BEC22744E0B101E2C"
                    "4060E7B08F6341657DAD9BC3EE02207D1489C7395DB018"
                    "8D3A56A977ECBA54B36FA9371B40319655B1B4429E33EF2D"
                ),
            ),
            "031D58EB48B4420B1F7B9DF55087E0E29FEF0E8468F9A6825B01CA2C361042D435",
        )
        self.assertFalse(output)

    def test_is_valid_message_ed25519_bad_sig(self):
        output = keypairs.is_valid_message(
            b"test message",
            bytes.fromhex(
                (
                    "CB199E1BFD4E3DAA105E4832EEDFA36413E1F442"
                    "05E4EFB9E27E826044C21E3E2E848BBC8195E895"
                    "9BADF887599B7310AD1B7047EF11B682E0D068F73749750F"
                ),
            ),
            "ED01FA53FA5A7E77798F882ECE20B1ABC00BB358A9E55A202D0D0676BD0CE37A63",
        )
        self.assertFalse(output)

    def test_is_valid_message_secp256k1_bad_sig(self):
        output = keypairs.is_valid_message(
            b"test message",
            bytes.fromhex(
                (
                    "30440220583A91C95E54E6A651C47BEC22744E0B101E2C"
                    "4060E7B08F6341657DAD9BC3EE02207D1489C7395DB018"
                    "8D3A56A977ECBA54B36FA9371B40319655B1B4429E33EF2F"
                ),
            ),
            "030D58EB48B4420B1F7B9DF55087E0E29FEF0E8468F9A6825B01CA2C361042D435",
        )
        self.assertFalse(output)
