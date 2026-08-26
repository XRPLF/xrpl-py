import json
import warnings
from unittest import TestCase

from xrpl.models.currencies import IssuedCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.vault_create import VaultCreate, VaultKind
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
            scale=4,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_close_ended_vault(self):
        # XLS-587: close-ended vault with subscription/redemption windows.
        tx = VaultCreate(
            account=_ACCOUNT,
            asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
            assets_maximum="1000",
            vault_kind=VaultKind.CLOSED,
            subscription_date=800000000,
            redemption_date=810000000,
        )
        self.assertTrue(tx.is_valid())
        tx_json = tx.to_xrpl()
        self.assertEqual(tx_json["VaultKind"], 1)
        self.assertEqual(tx_json["SubscriptionDate"], 800000000)
        self.assertEqual(tx_json["RedemptionDate"], 810000000)

    def test_valid_open_ended_vault_kind_int(self):
        # vault_kind accepts a plain int as well as the VaultKind enum.
        tx = VaultCreate(
            account=_ACCOUNT,
            asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
            vault_kind=0,
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.to_xrpl()["VaultKind"], 0)

    def test_close_ended_vault_requires_both_dates(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultCreate(
                account=_ACCOUNT,
                asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
                vault_kind=VaultKind.CLOSED,
                subscription_date=800000000,
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "vault_kind": "A close-ended vault requires both subscription_date "
                    "and redemption_date."
                }
            ),
        )

    def test_open_ended_vault_forbids_dates(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultCreate(
                account=_ACCOUNT,
                asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
                subscription_date=800000000,
                redemption_date=810000000,
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "vault_kind": "subscription_date and redemption_date can only be "
                    "set on a close-ended vault (vault_kind=1)."
                }
            ),
        )

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
                    "mptoken_metadata": (
                        "Metadata must be valid non-empty hex string less than 1024 "
                        "bytes (alternatively, 2048 hex characters)."
                    )
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

    def test_tx_emits_warning_for_missing_icon_metadata(self):
        invalid_metadata = {
            "ticker": "TBILL",
            "name": "T-Bill Yield Token",
            "icon": "https://example.org/tbill-icon.png",
            "uris": [
                {
                    "title": "Product Page",
                    "category": "website",
                }
            ],
        }

        tx = VaultCreate(
            account=_ACCOUNT,
            asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
            assets_maximum="1000",
            withdrawal_policy=1,
            mptoken_metadata=str_to_hex(json.dumps(invalid_metadata)),
        )

        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            valid = tx.is_valid()
            self.assertTrue(valid)
            self.assertTrue(len(caught_warnings) > 0, "Expected warning not emitted")
            warning_messages = [str(w.message) for w in caught_warnings]
            found = any(
                "- uris/us: should be an array of objects each with "
                "uri/u, category/c, and title/t properties." in msg
                for msg in warning_messages
            )
            self.assertTrue(
                found,
                "- uris/us: should be an array of objects each "
                "with uri/u, category/c, and title/t properties.",
            )

    def test_scale_field_too_large(self):
        with self.assertRaises(XRPLModelException) as error:
            VaultCreate(
                account=_ACCOUNT,
                asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
                assets_maximum="1000",
                withdrawal_policy=1,
                data=str_to_hex("A" * 256),
                scale=18 + 1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'VaultCreate': 'Scale field is higher than the allowed limit (18)'}",
        )

    def test_scale_field_too_small(self):
        with self.assertRaises(XRPLModelException) as error:
            VaultCreate(
                account=_ACCOUNT,
                asset=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
                assets_maximum="1000",
                withdrawal_policy=1,
                data=str_to_hex("A" * 256),
                scale=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'VaultCreate': 'Scale field is lower than the allowed limit (0)'}",
        )
