from unittest import TestCase
from unittest.mock import patch
import random
from xrpl import keypairs, addresscodec

RANDOM_BYTES = b",\x1f\xd4\xca'\xdf\x0b\xe7\x9c\x8b\xfeC\t\xdfX\x8e"
PLACEHOLDER_RETURN_VALUE = "dummy"


@patch("xrpl.addresscodec.encode_seed", autospec=True)
@patch("random.randbytes", autospec=True, return_value=RANDOM_BYTES)
class TestGenerateSeed(TestCase):
    def test_no_params(self, _randbytes, encode_seed):
        encode_seed.return_value = PLACEHOLDER_RETURN_VALUE
        output = keypairs.generate_seed()
        encode_seed.assert_called_once_with(
            RANDOM_BYTES,
            addresscodec.ED25519,
        )
        self.assertEqual(output, PLACEHOLDER_RETURN_VALUE)

    def test_entropy_provided(self, _randbytes, encode_seed):
        encode_seed.return_value = PLACEHOLDER_RETURN_VALUE
        entropy = "0123456789012345"
        output = keypairs.generate_seed(entropy)
        encode_seed.assert_called_once_with(
            entropy,
            addresscodec.ED25519,
        )
        self.assertEqual(output, PLACEHOLDER_RETURN_VALUE)

    def test_algorithm_provided(self, _randbytes, encode_seed):
        encode_seed.return_value = PLACEHOLDER_RETURN_VALUE
        algorithm = random.choice(addresscodec.ALGORITHMS)
        output = keypairs.generate_seed(algorithm=algorithm)
        encode_seed.assert_called_once_with(
            RANDOM_BYTES,
            algorithm,
        )
        self.assertEqual(output, PLACEHOLDER_RETURN_VALUE)
