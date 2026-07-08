from unittest import TestCase

import xrpl.core.binarycodec.types.currency as currency
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException

XRP_HEX_CODE = "0000000000000000000000000000000000000000"
# 'XRP' (0x585250) in the standard code position: renders as raw hex on decode
# (only 20 zero bytes mean XRP), matching rippled and xrpl.js.
XRP_IN_STANDARD_POSITION_HEX_CODE = "0000000000000000000000005852500000000000"
USD_HEX_CODE = "0000000000000000000000005553440000000000"
NONSTANDARD_HEX_CODE = "015841551A748AD2C1F76FF6ECB0CCCD00000000"
NOT_RECOMMENDED_HEX_CODE = "0000000000414C6F676F30330000000000000000"
# Standard layout but a non-ASCII code byte (0x80): raw hex, no raise (#1007).
NON_ASCII_CODE_HEX = "0000000000000000000000008000000000000000"
# Standard layout but a non-ASCII code byte (0xFF) between ASCII bytes (#1007).
MIXED_NON_ASCII_CODE_HEX = "00000000000000000000000041FF420000000000"
# ASCII 'USD' code but a non-zero trailing reserved byte: raw hex, not "USD"
# (#1006 -- must not be misclassified as the canonical USD code).
MALFORMED_USD_TRAILING_HEX = "0000000000000000000000005553440000000001"
XRP_ISO = "XRP"
USD_ISO = "USD"


class TestCurrency(TestCase):
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

    def test_construction_from_hex_nonrecommended(self):
        currency_object = currency.Currency.from_value(NOT_RECOMMENDED_HEX_CODE)
        self.assertEqual(currency_object.to_json(), NOT_RECOMMENDED_HEX_CODE)

    def test_raises_invalid_value_type(self):
        invalid_value = [1, 2, 3]
        self.assertRaises(
            XRPLBinaryCodecException, currency.Currency.from_value, invalid_value
        )

    def test_raises_unsupported_representation(self):
        # Encode-side validation is unchanged: a string that is neither a
        # 3-char ISO code nor a 40-char hex string is still rejected.
        for disallowed in ("INVALID", "XR", "12345", "GG"):
            self.assertRaises(
                XRPLBinaryCodecException,
                currency.Currency.from_value,
                disallowed,
            )

    def test_raises_invalid_hex_length(self):
        # A hex string of the wrong length remains an encode-side error.
        self.assertRaises(
            XRPLBinaryCodecException,
            currency.Currency.from_value,
            "00000000000000000000000055534400000000",  # 38 chars
        )

    def test_decode_never_raises_and_renders_hex(self):
        # #1006 / #1007: decoding any 20-byte buffer must never raise and must
        # render as raw uppercase hex when it is not XRP or a valid ISO code.
        for hex_code in (
            XRP_IN_STANDARD_POSITION_HEX_CODE,
            NON_ASCII_CODE_HEX,
            MIXED_NON_ASCII_CODE_HEX,
            MALFORMED_USD_TRAILING_HEX,
        ):
            currency_object = currency.Currency.from_value(hex_code)
            self.assertEqual(currency_object.to_json(), hex_code.upper())

    def test_xrp_in_standard_position_decodes_to_hex(self):
        # Bytes spelling 'XRP' in the code position render as raw hex on decode
        # (matching rippled and xrpl.js), rather than raising (#1007).
        currency_object = currency.Currency.from_value(
            XRP_IN_STANDARD_POSITION_HEX_CODE
        )
        self.assertEqual(currency_object.to_json(), XRP_IN_STANDARD_POSITION_HEX_CODE)

    def test_malformed_usd_is_not_iso(self):
        # #1006: a standard 'USD' code with a non-zero trailing reserved byte
        # must not be misclassified as the canonical USD ISO code.
        currency_object = currency.Currency.from_value(MALFORMED_USD_TRAILING_HEX)
        self.assertEqual(currency_object.to_json(), MALFORMED_USD_TRAILING_HEX)
        self.assertNotEqual(currency_object.to_json(), USD_ISO)

    def test_canonical_codes_still_decode_to_iso(self):
        # Canonical USD and all-zero XRP still resolve to their ISO codes.
        self.assertEqual(currency.Currency.from_value(USD_HEX_CODE).to_json(), USD_ISO)
        self.assertEqual(currency.Currency.from_value(XRP_HEX_CODE).to_json(), XRP_ISO)

    def test_decode_round_trip(self):
        # #1006 / #1007: for every malformed case, the bytes survive
        # Currency(bytes) -> to_json() -> Currency.from_value(hex).
        for hex_code in (
            XRP_HEX_CODE,
            USD_HEX_CODE,
            XRP_IN_STANDARD_POSITION_HEX_CODE,
            NON_ASCII_CODE_HEX,
            MIXED_NON_ASCII_CODE_HEX,
            MALFORMED_USD_TRAILING_HEX,
            NONSTANDARD_HEX_CODE,
            NOT_RECOMMENDED_HEX_CODE,
        ):
            original = currency.Currency.from_value(hex_code)
            round_tripped = currency.Currency.from_value(original.to_json())
            self.assertEqual(round_tripped.buffer, original.buffer)
            self.assertEqual(round_tripped.buffer.hex().upper(), hex_code.upper())

    def test_iso_code_from_hex_never_raises(self):
        # Direct unit check: non-ASCII and 'XRP' code bytes yield None, never
        # a UnicodeDecodeError or XRPLBinaryCodecException (#1007).
        self.assertIsNone(currency._iso_code_from_hex(b"\x80\x00\x00"))
        self.assertIsNone(currency._iso_code_from_hex(b"\x41\xff\x42"))
        self.assertIsNone(currency._iso_code_from_hex(b"XRP"))
        self.assertEqual(currency._iso_code_from_hex(b"USD"), "USD")
