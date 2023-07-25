from unittest import TestCase

from xrpl.models.currencies import XRP
from xrpl.utils import xrp_to_drops


class TestXRP(TestCase):
    def test_to_dict(self):
        self.assertEqual(XRP().to_dict()["currency"], "XRP")

    def test_to_amount(self):
        amount = 12
        expected = xrp_to_drops(amount)
        result = XRP().to_amount(amount)

        self.assertEqual(result, expected)
