import json
import warnings
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import MPTokenIssuanceCreate, MPTokenIssuanceCreateFlag
from xrpl.utils import str_to_hex

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
            mptoken_metadata=str_to_hex(json.dumps(mptoken_metadata)),
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

    def test_transfer_fee_out_of_range_lower(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceCreate(
                account=_ACCOUNT,
                maximum_amount="9223372036854775807",  # "7fffffffffffffff"
                transfer_fee=-1,
                flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'transfer_fee': 'Field must be between 0 and 50000'}",
        )

    def test_transfer_fee_out_of_range_greater(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceCreate(
                account=_ACCOUNT,
                maximum_amount="9223372036854775807",  # "7fffffffffffffff"
                transfer_fee=50001,
                flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'transfer_fee': 'Field must be between 0 and 50000'}",
        )

    def test_mptoken_metadata_empty_string(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceCreate(
                account=_ACCOUNT,
                flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
                mptoken_metadata="",
            )
        self.assertEqual(
            error.exception.args[0],
            (
                "{'mptoken_metadata': 'Metadata must be valid non-empty hex string "
                "less than 1024 bytes (alternatively, 2048 hex characters).'}"
            ),
        )

    def test_mptoken_metadata_not_hex(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceCreate(
                account=_ACCOUNT,
                flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
                mptoken_metadata="http://xrpl.org",
            )
        self.assertEqual(
            error.exception.args[0],
            (
                "{'mptoken_metadata': 'Metadata must be valid non-empty hex string "
                "less than 1024 bytes (alternatively, 2048 hex characters).'}"
            ),
        )

    def test_tx_emits_warning_for_missing_icon_metadata(self):
        invalid_metadata = {
            "ticker": "TBILL",
            "name": "T-Bill Yield Token",
            "invalid_field": "should cause warning",
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
                "- icon is required and must be string." in msg
                for msg in warning_messages
            )
            self.assertTrue(found, "- icon is required and must be string.")
