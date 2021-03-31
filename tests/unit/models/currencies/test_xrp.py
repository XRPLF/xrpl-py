from unittest import TestCase

from xrpl.models.currencies import XRP


class TestXRP(TestCase):
    def test_to_dict(self):
        self.assertEqual(XRP().to_dict()["currency"], "XRP")
