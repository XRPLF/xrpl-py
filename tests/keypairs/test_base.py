from unittest import TestCase
from unittest.mock import patch
from xrpl import keypairs, addresscodec

RANDOM_BYTES = b",\x1f\xd4\xca'\xdf\x0b\xe7\x9c\x8b\xfeC\t\xdfX\x8e"


@patch("xrpl.addresscodec.encode_seed", autospec=True)
class TestGenerateSeed(TestCase):
    @patch("random.randbytes", autospec=True, return_value=RANDOM_BYTES)
    def test_no_params(self, _randbytes, encode_seed):
        keypairs.generate_seed()
        encode_seed.assert_called_once_with(
            RANDOM_BYTES,
            addresscodec.ED25519,
        )

    def test_valid_entropy(self, encode_seed):
        entropy = "0123456789012345"
        keypairs.generate_seed(entropy)
        encode_seed.assert_called_once_with(
            entropy,
            addresscodec.ED25519,
        )

    def test_invalid_entropy(self, _encode_seed):
        entropy = "0"
        with self.assertRaises(keypairs.exceptions.XRPLKeypairsException):
            keypairs.generate_seed(entropy)
