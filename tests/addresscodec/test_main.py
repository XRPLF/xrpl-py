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

            classic_address, tag, is_test_network = addresscodec.decode_xaddress(
                xaddress
            )
            self.assertEqual(classic_address, expected_classic_address_bytes)
            self.assertEqual(tag, expected_tag)
            self.assertTrue(is_test_network)

            # main
            xaddress = addresscodec.encode_xaddress(
                expected_classic_address_bytes, expected_tag, False
            )
            self.assertEqual(xaddress, expected_main_xaddress)

            classic_address, tag, is_test_network = addresscodec.decode_xaddress(
                xaddress
            )
            self.assertEqual(classic_address, expected_classic_address_bytes)
            self.assertEqual(tag, expected_tag)
            self.assertFalse(is_test_network)

    def test_classic_address_to_xaddress(self):
        for test_case in test_cases:
            (
                classic_address,
                tag,
                expected_main_xaddress,
                expected_test_xaddress,
            ) = test_case

            # test
            xaddress = addresscodec.classic_address_to_xaddress(
                classic_address, tag, True
            )
            self.assertEqual(xaddress, expected_test_xaddress)

            # main
            xaddress = addresscodec.classic_address_to_xaddress(
                classic_address, tag, False
            )
            self.assertEqual(xaddress, expected_main_xaddress)

    def test_xaddress_to_classic_address(self):
        for test_case in test_cases:
            (
                expected_classic_address,
                expected_tag,
                main_xaddress,
                test_xaddress,
            ) = test_case

            # test
            classic_address, tag, is_test = addresscodec.xaddress_to_classic_address(
                test_xaddress
            )
            self.assertEqual(classic_address, expected_classic_address)
            self.assertEqual(tag, expected_tag)
            self.assertTrue(is_test)

            # main
            classic_address, tag, is_test = addresscodec.xaddress_to_classic_address(
                main_xaddress
            )
            self.assertEqual(classic_address, expected_classic_address)
            self.assertEqual(tag, expected_tag)
            self.assertFalse(is_test)

    def test_classic_address_to_xaddress_invalid_tag(self):
        classic_address = "rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf"
        tag = addresscodec.MAX_32_BIT_UNSIGNED_INT + 1

        self.assertRaises(
            addresscodec.XRPLAddressCodecException,
            addresscodec.classic_address_to_xaddress,
            classic_address,
            tag,
            True,
        )

        self.assertRaises(
            addresscodec.XRPLAddressCodecException,
            addresscodec.classic_address_to_xaddress,
            classic_address,
            tag,
            False,
        )

    def test_classic_address_to_xaddress_bad_classic_address(self):
        classic_address = "r"

        self.assertRaises(
            ValueError,
            addresscodec.classic_address_to_xaddress,
            classic_address,
            None,
            True,
        )

        self.assertRaises(
            ValueError,
            addresscodec.classic_address_to_xaddress,
            classic_address,
            None,
            False,
        )
