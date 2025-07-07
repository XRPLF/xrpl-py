from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.vault_delete import VaultDelete

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_VAULT_ID = "B982D2AAEF6014E6BE3194D939865453D56D16FF7081BB1D0ED865C708ABCEEE"


class TestVaultDelete(TestCase):
    def test_valid(self):
        tx = VaultDelete(
            account=_ACCOUNT,
            vault_id=_VAULT_ID,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_vault_id_field(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultDelete(
                account=_ACCOUNT,
                vault_id="0",
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "vault_id": "Invalid vault ID: Length must be 32 characters "
                    "(64 hex characters)."
                }
            ),
        )
