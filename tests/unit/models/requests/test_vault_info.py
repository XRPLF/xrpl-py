from unittest import TestCase

from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import VaultInfo
from xrpl.models.requests.request import _DEFAULT_API_VERSION

_ASSET = XRP()
_ASSET_2 = IssuedCurrency(currency="USD", issuer="rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj")
_ACCOUNT = _ASSET_2.issuer

VAULT_ID = "CE47F59928D43773A8A9CB7F525BE031977EFB72A23FF094C1C326E687D2B567"


class TestVaultInfo(TestCase):
    def test_valid_vault_info(self):
        request = VaultInfo(
            vault_id=VAULT_ID,
        )
        self.assertTrue(request.is_valid())

    def test_specify_invalid_combination_of_input_fields_1(self):
        with self.assertRaises(ValueError):
            VaultInfo()

    def test_specify_invalid_combination_of_input_fields_2(self):
        with self.assertRaises(ValueError):
            VaultInfo(
                vault_id=VAULT_ID,
                owner="rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj",
                seq=1234567890,
            )
