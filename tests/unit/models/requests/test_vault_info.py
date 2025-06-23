from unittest import TestCase

from xrpl.models.requests import VaultInfo

VAULT_ID = "CE47F59928D43773A8A9CB7F525BE031977EFB72A23FF094C1C326E687D2B567"


class TestVaultInfo(TestCase):
    def test_valid_vault_info(self):
        request = VaultInfo(
            vault_id=VAULT_ID,
        )
        self.assertTrue(request.is_valid())

    def test_vault_info_requires_parameters(self):
        with self.assertRaises(ValueError):
            VaultInfo()

    def test_vault_info_rejects_conflicting_parameters(self):
        with self.assertRaises(ValueError):
            VaultInfo(
                vault_id=VAULT_ID,
                owner="rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj",
                seq=1234567890,
            )

    def test_valid_vault_info_with_owner_and_seq(self):
        request = VaultInfo(
            owner="rN6zcSynkRnf8zcgTVrRL8K7r4ovE7J4Zj",
            seq=1234567890,
        )
        self.assertTrue(request.is_valid())
