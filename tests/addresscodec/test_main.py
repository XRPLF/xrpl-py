import unittest

from xrpl import addresscodec
from .test_main_testcases import testcases


class TestMain(unittest.TestCase):
    def test_encode_xaddress(self):
        for testcase in testcases:
            (
                classic_address,
                tag,
                expected_main_xaddress,
                expected_test_xaddress,
            ) = testcase
            decoded_classic_address = addresscodec.decode_classic_address(
                classic_address
            )

            # test
            xaddress = addresscodec.encode_xaddress(decoded_classic_address, tag, True)
            self.assertEqual(xaddress, expected_test_xaddress)

            # main
            xaddress = addresscodec.encode_xaddress(decoded_classic_address, tag, False)
            self.assertEqual(xaddress, expected_main_xaddress)

    def test_classic_address_to_xaddress(self):
        for testcase in testcases:
            (
                classic_address,
                tag,
                expected_main_xaddress,
                expected_test_xaddress,
            ) = testcase

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
