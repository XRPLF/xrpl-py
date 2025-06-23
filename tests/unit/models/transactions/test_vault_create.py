from unittest import TestCase

from xrpl.models.currencies import IssuedCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.vault_create import VaultCreate
from xrpl.utils import str_to_hex

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"


class TestVaultCreate(TestCase):
    def test_valid(self):
        tx = VaultCreate(
            account=_ACCOUNT,
            asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
            assets_maximum="1000",
            withdrawal_policy=1,
            data=str_to_hex("A" * 256),
        )
        self.assertTrue(tx.is_valid())

    def test_long_data_field(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultCreate(
                account=_ACCOUNT,
                asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
                assets_maximum="1000",
                withdrawal_policy=1,
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

    def test_long_mpt_metadata_field(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultCreate(
                account=_ACCOUNT,
                asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
                assets_maximum="1000",
                withdrawal_policy=1,
                # Note: MPTMetadata is associated with a Multi-Purpose token and not a
                # conventional IOU token. This unit test demonstrates the validity of
                # the transaction model only. It must not be misconstrued as an
                # archetype of a VaultCreate transaction.
                mptoken_metadata=str_to_hex("A" * 1025),
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "mptoken_metadata": "Metadata must be less than 1024 bytes "
                    "(alternatively, 2048 hex characters)."
                }
            ),
        )

    def test_invalid_domain_id_field(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultCreate(
                account=_ACCOUNT,
                asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
                assets_maximum="1000",
                withdrawal_policy=1,
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
