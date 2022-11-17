from unittest import TestCase

from xrpl.models.currencies.issue import Issue
from xrpl.models.requests import AMMInfo

_ASSET = Issue(currency="XRP")
_ASSET_2 = Issue(currency="USD", issuer="rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj")


class TestAMMInfo(TestCase):
    def test_asset_asset2(self):
        request = AMMInfo(
            asset=_ASSET,
            asset2=_ASSET_2,
        )
        self.assertTrue(request.is_valid())
