import unittest

from xrpl import addresscodec
from .test_main_testcases import testcases

class TestMain(unittest.TestCase):
    def test_encode_xaddress(self):
        for testcase in testcases:
            classic_address, tag, expected_main_xaddress, expected_test_xaddress = testcase
            decoded_classic_address = addresscodec.decode_classic_address(classic_address)
            
            # test
            xaddress = addresscodec.encode_xaddress(decoded_classic_address, tag, True)
            self.assertEqual(xaddress, expected_test_xaddress)

            # main
            xaddress = addresscodec.encode_xaddress(decoded_classic_address, tag, False)
            self.assertEqual(xaddress, expected_main_xaddress)