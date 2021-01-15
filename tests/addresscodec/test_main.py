import unittest

from xrpl import addresscodec
from .test_main_test_cases import test_cases


class TestMain(unittest.TestCase):
    def test_xaddress_encode_decode(self):
        for test_case in test_cases:
            (
                expected_classic_address,
                expected_tag,
                expected_main_xaddress,
                expected_test_xaddress,
            ) = test_case
            expected_classic_address_bytes = addresscodec.decode_classic_address(
                expected_classic_address
            )

            # test
            xaddress = addresscodec.encode_xaddress(
                expected_classic_address_bytes, expected_tag, True
            )
            self.assertEqual(xaddress, expected_test_xaddress)

            classic_address, tag, is_test = addresscodec.decode_xaddress(xaddress)
            self.assertEqual(classic_address, expected_classic_address_bytes)
            self.assertEqual(tag, expected_tag)
            self.assertTrue(is_test)

            # main
            xaddress = addresscodec.encode_xaddress(
                expected_classic_address_bytes, expected_tag, False
            )
            self.assertEqual(xaddress, expected_main_xaddress)

            classic_address, tag, is_test = addresscodec.decode_xaddress(xaddress)
            self.assertEqual(classic_address, expected_classic_address_bytes)
            self.assertEqual(tag, expected_tag)
            self.assertFalse(is_test)
