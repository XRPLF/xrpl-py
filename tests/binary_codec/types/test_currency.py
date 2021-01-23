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
