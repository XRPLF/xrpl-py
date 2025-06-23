from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.vault_set import VaultSet
from xrpl.utils import str_to_hex

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_VAULT_ID = "DB303FC1C7611B22C09E773B51044F6BEA02EF917DF59A2E2860871E167066A5"


class TestVaultSet(TestCase):
    def test_valid(self):
        tx = VaultSet(
            account=_ACCOUNT,
            vault_id=_VAULT_ID,
            assets_maximum="1000",
            data=str_to_hex("A" * 256),
        )
        self.assertTrue(tx.is_valid())

    def test_long_data_field(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultSet(
                account=_ACCOUNT,
                vault_id=_VAULT_ID,
                data=str_to_hex("A" * 257),
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "data": "Data must be less than 256 bytes "
                    "(alternatively, 512 hex characters)."
                }
            ),
        )

    def test_invalid_domain_id_field(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultSet(
                account=_ACCOUNT,
                vault_id=_VAULT_ID,
                domain_id="A" * 14,
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "domain_id": "Invalid domain ID: Length must be 32 characters "
                    "(64 hex characters)."
                }
            ),
        )
