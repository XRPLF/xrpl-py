from unittest import TestCase

from xrpl.models.currencies import XRP
from xrpl.models.exceptions import XRPLModelValidationException


class TestXRP(TestCase):
    def test_currency_default_valid(self):
        obj = XRP()
        self.assertTrue(obj.is_valid())

    def test_currency_xrp_valid(self):
        obj = XRP(currency="XRP")
        self.assertTrue(obj.is_valid())

    def test_currency_mixed_xrp_valid(self):
        obj = XRP(currency="XrP")
        self.assertTrue(obj.is_valid())

    def test_currency_lower_xrp_valid(self):
        obj = XRP(currency="xrp")
        self.assertTrue(obj.is_valid())

    def test_currency_non_xrp_invalid(self):
        with self.assertRaises(XRPLModelValidationException):
            XRP(currency="usd")
