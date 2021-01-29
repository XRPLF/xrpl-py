from unittest import TestCase
from unittest.mock import patch

from xrpl import CryptoAlgorithm, keypairs
from xrpl.keypairs.exceptions import XRPLKeypairsException

DUMMY_BYTES = b"\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10"


class TestMain(TestCase):
    # unfortunately, this patching is very brittle; it depends on the syntax
    # used to import secrets within the calling module.
    @patch("xrpl.keypairs.main.token_bytes", autospec=True, return_value=DUMMY_BYTES)
    def test_generate_seed_no_params(self, _randbytes):
        output = keypairs.generate_seed()
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_entropy_provided(self):
        output = keypairs.generate_seed(DUMMY_BYTES.decode("UTF-8"))
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_ed25519(self):
        output = keypairs.generate_seed(
            DUMMY_BYTES.decode("UTF-8"), CryptoAlgorithm.ED25519
        )
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_secp256k1(self):
        output = keypairs.generate_seed(
            DUMMY_BYTES.decode("UTF-8"), CryptoAlgorithm.SECP256K1
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

    def test_derive_keypair_validator(self):
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
