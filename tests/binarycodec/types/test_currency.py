import unittest

import xrpl.binarycodec.types.currency as currency
from xrpl.binarycodec.exceptions import XRPLBinaryCodecException

XRP_HEX_CODE = "0000000000000000000000000000000000000000"
USD_HEX_CODE = "0000000000000000000000005553440000000000"
NONSTANDARD_HEX_CODE = "1" * 40
XRP_ISO = "XRP"
USD_ISO = "USD"


class TestCurrency(unittest.TestCase):
    def test_is_iso_code(self):
        valid_code = "ABC"
        valid_code_numeric = "123"
        invalid_code_long = "LONG"
        invalid_code_short = "NO"
        self.assertTrue(currency._is_iso_code(valid_code))
        self.assertTrue(currency._is_iso_code(valid_code_numeric))
        self.assertFalse(currency._is_iso_code(invalid_code_long))
        self.assertFalse(currency._is_iso_code(invalid_code_short))

    def test_is_hex(self):
        # Valid = 40 char length and only valid hex chars
        valid_hex = "0000000000000000000000005553440000000000"
        invalid_hex_long = "0000000000000000000000005553440000000000123455"
        invalid_hex_short = "1234"
        invalid_hex_chars = "USD0000000000000000000005553440000000000"
        self.assertTrue(currency._is_hex(valid_hex))
        self.assertFalse(currency._is_hex(invalid_hex_long))
        self.assertFalse(currency._is_hex(invalid_hex_short))
        self.assertFalse(currency._is_hex(invalid_hex_chars))

    def test_iso_to_bytes(self):
        # Valid non-XRP
        usd_iso_bytes = currency._iso_to_bytes(USD_ISO)
        # convert bytes to hex string for comparison to expectation
        self.assertEqual(usd_iso_bytes.hex(), USD_HEX_CODE)

        # Valid XRP
        xrp_iso_bytes = currency._iso_to_bytes(XRP_ISO)
        # convert bytes to hex string for comparison to expectation
        self.assertEqual(xrp_iso_bytes.hex(), XRP_HEX_CODE)

        # Error case
        invalid_iso = "INVALID"
        self.assertRaises(XRPLBinaryCodecException, currency._iso_to_bytes, invalid_iso)

    def test_construction_from_hex_standard(self):
        # XRP case
        currency_object = currency.Currency.from_value(XRP_HEX_CODE)
        self.assertEqual(currency_object.to_json(), XRP_ISO)

        # General case
        currency_object = currency.Currency.from_value(USD_HEX_CODE)
        self.assertEqual(currency_object.to_json(), USD_ISO)

    def test_construction_from_iso_code_standard(self):
        # XRP case
        currency_object = currency.Currency.from_value(XRP_ISO)
        self.assertEqual(currency_object.to_hex(), XRP_HEX_CODE)

        # General case
        currency_object = currency.Currency.from_value(USD_ISO)
        self.assertEqual(currency_object.to_hex(), USD_HEX_CODE)

    def test_construction_from_hex_nonstandard(self):
        currency_object = currency.Currency.from_value(NONSTANDARD_HEX_CODE)
        self.assertEqual(currency_object.to_json(), NONSTANDARD_HEX_CODE)
