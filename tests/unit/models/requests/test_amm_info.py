from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import AMMInfo

_AMM_ID = "5DB01B7FFED6B67E6B0414DED11E051D2EE2B7619CE0EAA6286D67A3A4D5BDB3"
_ASSET_1 = "1000"
_ASSET_2 = IssuedCurrencyAmount(
    currency="USD", issuer="rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj", value="100"
)


class TestAMMInfo(TestCase):
    def test_amm_id(self):
        request = AMMInfo(
            AMMID=_AMM_ID,
        )
        self.assertTrue(request.is_valid())

    def test_asset1_asset2(self):
        request = AMMInfo(
            Asset1=_ASSET_1,
            Asset2=_ASSET_2,
        )
        self.assertTrue(request.is_valid())

    def test_no_params_is_invalid(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMInfo()
        self.assertEqual(
            error.exception.args[0],
            "{'AMMInfo': 'Must set either `AMMID` or both `Asset1` and `Asset2`'}",
        )

    def test_missing_asset1_is_invalid(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMInfo(
                Asset2=_ASSET_2,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMInfo': 'Missing `Asset1`. Must set both `Asset1` and `Asset2`'}",
        )

    def test_missing_asset2_is_invalid(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMInfo(
                Asset1=_ASSET_1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMInfo': 'Missing `Asset2`. Must set both `Asset1` and `Asset2`'}",
        )
