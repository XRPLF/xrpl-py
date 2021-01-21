from unittest import TestCase
from unittest.mock import patch

from xrpl import CryptoAlgorithm, keypairs

DUMMY_BYTES = b"\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10"


class TestMain(TestCase):
    # unfortunately, this patching is very brittle; it depends on the syntax
    # used to import random within the calling module.
    @patch("xrpl.keypairs.main.randbytes", autospec=True, return_value=DUMMY_BYTES)
    def test_generate_seed_no_params(self, _randbytes):
        output = keypairs.generate_seed()
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_entropy_provided(self):
        output = keypairs.generate_seed(DUMMY_BYTES)
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_ed25519(self):
        output = keypairs.generate_seed(DUMMY_BYTES, CryptoAlgorithm.ED25519)
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_secp256k1(self):
        output = keypairs.generate_seed(DUMMY_BYTES, CryptoAlgorithm.SECP256K1)
        self.assertEqual(output, "sp5fghtJtpUorTwvof1NpDXAzNwf5")

    def test_derive_ed25519(self):
        public, private = keypairs.derive("sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")
        self.assertEqual(
            public,
            "ED01FA53FA5A7E77798F882ECE20B1ABC00BB358A9E55A202D0D0676BD0CE37A63",
        )
        self.assertEqual(
            private,
            "EDB4C4E046826BD26190D09715FC31F4E6A728204EADD112905B08B14B7F15C4F3",
        )
