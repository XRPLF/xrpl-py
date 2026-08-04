import json
import warnings
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import (
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
    MPTokenIssuanceImmutableFlag,
)
from xrpl.utils import str_to_hex
from xrpl.utils.mptoken_metadata import encode_mptoken_metadata

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"


class TestMPTokenIssuanceCreate(TestCase):
    def test_tx_is_valid(self):
        mptoken_metadata = {
            "ticker": "TBILL",
            "name": "T-Bill Yield Token",
            "icon": "https://example.org/tbill-icon.png",
            "asset_class": "rwa",
            "asset_subclass": "treasury",
            "issuer_name": "Example Yield Co.",
        }
        tx = MPTokenIssuanceCreate(
            account=_ACCOUNT,
            maximum_amount="9223372036854775807",  # "7fffffffffffffff"
            asset_scale=2,
            transfer_fee=1,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK
            | MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            mptoken_metadata=encode_mptoken_metadata(mptoken_metadata),
        )
        self.assertTrue(tx.is_valid())

    def test_transfer_fee_without_can_transfer_flag(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceCreate(
                account=_ACCOUNT,
                maximum_amount="9223372036854775807",  # "7fffffffffffffff"
                transfer_fee=1,
                flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'transfer_fee': 'Field cannot be provided without enabling "
            "tfMPTCanTransfer flag.'}",
        )

    def test_transfer_fee_out_of_range_fails(self):
        for fee in (-1, 50001):
            with self.subTest(transfer_fee=fee):
                with self.assertRaises(XRPLModelException) as error:
                    MPTokenIssuanceCreate(
                        account=_ACCOUNT,
                        maximum_amount="9223372036854775807",  # "7fffffffffffffff"
                        transfer_fee=fee,
                        flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
                    )
                self.assertEqual(
                    error.exception.args[0],
                    "{'transfer_fee': 'Field must be between 0 and 50000'}",
                )

    def test_mptoken_metadata_invalid_fails(self):
        for metadata in ("", "http://xrpl.org"):
            with self.subTest(metadata=metadata):
                with self.assertRaises(XRPLModelException) as error:
                    MPTokenIssuanceCreate(
                        account=_ACCOUNT,
                        flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
                        mptoken_metadata=metadata,
                    )
                self.assertEqual(
                    error.exception.args[0],
                    (
                        "{'mptoken_metadata': 'Metadata must be valid non-empty hex "
                        "string less than 1024 bytes (alternatively, 2048 hex "
                        "characters).'}"
                    ),
                )

    def test_tx_emits_warning_for_missing_icon_metadata(self):
        invalid_metadata = {
            "ticker": "TBILL",
            "name": "T-Bill Yield Token",
            "icon": "https://example.org/tbill-icon.png",
            "asset_class": "rwa",
            "asset_subclass": None,
            "issuer_name": "Example Yield Co.",
        }

        tx = MPTokenIssuanceCreate(
            account=_ACCOUNT,
            mptoken_metadata=str_to_hex(json.dumps(invalid_metadata)),
        )

        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            valid = tx.is_valid()
            self.assertTrue(valid)
            self.assertTrue(len(caught_warnings) > 0, "Expected warning not emitted")
            warning_messages = [str(w.message) for w in caught_warnings]
            found = any(
                "- asset_subclass/as: required when asset_class is rwa." in msg
                for msg in warning_messages
            )
            self.assertTrue(
                found, "- asset_subclass/as: required when asset_class is rwa."
            )

    # DynamicMPT tests
    def test_tx_with_all_immutable_flags(self):
        """All ImmutableFlags bits combined are valid."""
        all_flags = 0
        for flag in MPTokenIssuanceImmutableFlag:
            all_flags |= flag.value
        tx = MPTokenIssuanceCreate(account=_ACCOUNT, immutable_flags=all_flags)
        self.assertTrue(tx.is_valid())

    def test_tx_immutable_flags_invalid_fails(self):
        # Reserved bit 0x00000001, and 0 (nothing declared immutable)
        cases = [
            (0x00000001, "immutable_flags contains invalid or reserved bits"),
            (0, "immutable_flags cannot be 0"),
        ]
        for value, message in cases:
            with self.subTest(immutable_flags=value):
                with self.assertRaises(XRPLModelException) as error:
                    MPTokenIssuanceCreate(account=_ACCOUNT, immutable_flags=value)
                self.assertIn(message, error.exception.args[0])
