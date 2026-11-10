from unittest import TestCase

from xrpl.models.currencies import XRP, IssuedCurrency, MPTCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import AMMInfo
from xrpl.models.requests.request import _DEFAULT_API_VERSION

_ASSET = XRP()
_ASSET_2 = IssuedCurrency(currency="USD", issuer="rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj")
_ACCOUNT = _ASSET_2.issuer


class TestAMMInfo(TestCase):
    def test_populate_api_version_field(self):
        request = AMMInfo(
            asset=_ASSET,
            asset2=_ASSET_2,
        )
        self.assertEqual(request.api_version, _DEFAULT_API_VERSION)
        self.assertTrue(request.is_valid())

    def test_asset_asset2(self):
        request = AMMInfo(
            asset=_ASSET,
            asset2=_ASSET_2,
        )
        self.assertTrue(request.is_valid())

    def test_amount(self):
        request = AMMInfo(
            amm_account=_ACCOUNT,
        )
        self.assertTrue(request.is_valid())

    def test_all_three(self):
        with self.assertRaises(XRPLModelException):
            AMMInfo(
                amm_account=_ACCOUNT,
                asset=_ASSET,
                asset2=_ASSET_2,
            )

    def test_only_asset(self):
        with self.assertRaises(XRPLModelException):
            AMMInfo(
                asset=_ASSET,
            )

    def test_only_one_asset2(self):
        with self.assertRaises(XRPLModelException):
            AMMInfo(
                asset2=_ASSET_2,
            )

    def test_mpt_assets(self):
        mpt_asset = MPTCurrency(
            mpt_issuance_id="00000003430427B80BD2D09D36B70B969E12801065F22308"
        )
        request = AMMInfo(asset=mpt_asset, asset2=_ASSET)
        self.assertTrue(request.is_valid())
        self.assertEqual(request.to_dict()["asset"], mpt_asset.to_dict())
