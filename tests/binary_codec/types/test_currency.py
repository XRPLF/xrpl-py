import unittest

import xrpl.binary_codec.types.currency as currency


class TestCurrency(unittest.TestCase):
    def setUp(self):
        pass

    def test_is_iso_code(self):
        valid_code = "USD"
        valid_code_numeric = "123"
        invalid_code_long = "LONG"
        invalid_code_short = "NO"
        self.assertTrue(currency.is_iso_code(valid_code))
        self.assertTrue(currency.is_iso_code(valid_code_numeric))
        self.assertFalse(currency.is_iso_code(invalid_code_long))
        self.assertFalse(currency.is_iso_code(invalid_code_short))

    def test_is_hex(self):
        valid_hex = (
            "0000000000000000000000005553440000000000"  # USD iso code hex-encoded
        )
        invalid_hex_long = "0000000000000000000000005553440000000000123455"
        invalid_hex_short = "1234"
        invalid_hex_chars = "USD0000000000000000000005553440000000000"
        self.assertTrue(currency.is_hex(valid_hex))
        self.assertFalse(currency.is_hex(invalid_hex_long))
        self.assertFalse(currency.is_hex(invalid_hex_short))
        self.assertFalse(currency.is_hex(invalid_hex_chars))
