from unittest import TestCase
from unittest.mock import patch
from xrpl import keypairs, addresscodec

DUMMY_BYTES = b"\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10"


class TestMain(TestCase):
    @patch("random.randbytes", autospec=True, return_value=DUMMY_BYTES)
    def test_generate_seed_no_params(self, _randbytes):
        output = keypairs.generate_seed()
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_entropy_provided(self):
        output = keypairs.generate_seed(DUMMY_BYTES)
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_ed25519(self):
        output = keypairs.generate_seed(DUMMY_BYTES, addresscodec.ED25519)
        self.assertEqual(output, "sEdSKaCy2JT7JaM7v95H9SxkhP9wS2r")

    def test_generate_seed_secp256k1(self):
        output = keypairs.generate_seed(DUMMY_BYTES, addresscodec.SECP256K1)
        self.assertEqual(output, "sp5fghtJtpUorTwvof1NpDXAzNwf5")
