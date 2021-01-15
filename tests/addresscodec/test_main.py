import unittest

from xrpl import addresscodec
from .test_main_test_cases import test_cases


class TestMain(unittest.TestCase):
    def test_encode_xaddress(self):
        # TODO: make these separate tests somehow
        for test_case in test_cases:
            (
                classic_address,
                tag,
                expected_main_xaddress,
                expected_test_xaddress,
            ) = test_case
            decoded_classic_address = addresscodec.decode_classic_address(
                classic_address
            )

            # test
            xaddress = addresscodec.encode_xaddress(decoded_classic_address, tag, True)
            self.assertEqual(xaddress, expected_test_xaddress)

            # main
            xaddress = addresscodec.encode_xaddress(decoded_classic_address, tag, False)
            self.assertEqual(xaddress, expected_main_xaddress)
