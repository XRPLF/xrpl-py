from unittest import TestCase

from xrpl.models.currencies import XRP


class TestXRP(TestCase):
    def test_to_dict(self):
        self.assertEqual(XRP().to_dict()["currency"], "XRP")

    def test_to_amount(self):
        amount = "12"
        issued_currency_amount = XRP().to_amount(amount)

        self.assertEqual(issued_currency_amount, amount)
