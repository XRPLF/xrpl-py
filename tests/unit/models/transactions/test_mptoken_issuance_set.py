import json
import warnings
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import MPTokenIssuanceSet
from xrpl.models.transactions.mptoken_issuance_set import (
    MPTokenIssuanceSetFlag,
    MPTokenIssuanceSetMutableFlag,
)
from xrpl.utils import str_to_hex

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_TOKEN_ID = "000004C463C52827307480341125DA0577DEFC38405B0E3E"


class TestMPTokenIssuanceSet(TestCase):
    def test_valid_basic_transaction(self):
        """Test valid transaction with lock flag."""
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_holder(self):
        """Test valid transaction with holder field."""
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
            flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_without_flags(self):
        """Test valid transaction without flags (only tx fee deducted)."""
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
        )
        self.assertTrue(tx.is_valid())

    def test_lock_unlock_flag_conflict(self):
        """Test that TF_MPT_LOCK and TF_MPT_UNLOCK cannot both be set."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
                flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK
                | MPTokenIssuanceSetFlag.TF_MPT_UNLOCK,
            )
        self.assertIn(
            "flag conflict: both TF_MPT_LOCK and TF_MPT_UNLOCK can't be set",
            error.exception.args[0],
        )

    # DynamicMPT tests
    def test_valid_with_all_dynamic_fields(self):
        """Test valid transaction with all dynamic fields combined."""
        metadata = {"ticker": "TBILL", "name": "T-Bill", "icon": "https://ex.org/i.png"}
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK
            | MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_ESCROW,
            transfer_fee=200,
            mptoken_metadata=str_to_hex(json.dumps(metadata)),
        )
        self.assertTrue(tx.is_valid())

    def test_holder_with_dynamic_field_fails(self):
        """holder cannot be combined with any mutate-issuance field."""
        dynamic_fields = [
            {"mutable_flags": MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK},
            {"mptoken_metadata": "464F4F"},
            {"transfer_fee": 200},
        ]
        for field in dynamic_fields:
            with self.subTest(field=next(iter(field))):
                with self.assertRaises(XRPLModelException) as error:
                    MPTokenIssuanceSet(
                        account=_ACCOUNT,
                        mptoken_issuance_id=_TOKEN_ID,
                        holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
                        **field,
                    )
                self.assertIn("holder cannot be provided", error.exception.args[0])

    def test_mutable_flags_zero_fails(self):
        """Test that mutable_flags cannot be 0."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=0,
            )
        self.assertIn("mutable_flags cannot be 0", error.exception.args[0])

    def test_mutable_flags_invalid_bits_fail(self):
        """Unknown or reserved bits in mutable_flags are rejected."""
        cases = [
            0x00004000,  # undefined bit (0x1000/0x2000 are now confidential flags)
            MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK.value | 0x00010000,
        ]
        for value in cases:
            with self.subTest(mutable_flags=value):
                with self.assertRaises(XRPLModelException) as error:
                    MPTokenIssuanceSet(
                        account=_ACCOUNT,
                        mptoken_issuance_id=_TOKEN_ID,
                        mutable_flags=value,
                    )
                self.assertIn(
                    "mutable_flags contains invalid bits", error.exception.args[0]
                )

    def test_multiple_set_flags_valid(self):
        """Test that multiple distinct SET flags can be combined."""
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK
            | MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_REQUIRE_AUTH
            | MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_CLAWBACK,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_transfer_fee_values(self):
        """Valid transfer_fee values: mid-range, zero (removal), and the max."""
        for fee in (200, 0, 50000):
            with self.subTest(transfer_fee=fee):
                tx = MPTokenIssuanceSet(
                    account=_ACCOUNT,
                    mptoken_issuance_id=_TOKEN_ID,
                    transfer_fee=fee,
                )
                self.assertTrue(tx.is_valid())

    def test_transfer_fee_out_of_range_fails(self):
        """transfer_fee outside the 0..50000 range is rejected."""
        for fee in (-1, 50001):
            with self.subTest(transfer_fee=fee):
                with self.assertRaises(XRPLModelException) as error:
                    MPTokenIssuanceSet(
                        account=_ACCOUNT,
                        mptoken_issuance_id=_TOKEN_ID,
                        transfer_fee=fee,
                    )
                self.assertIn(
                    "transfer_fee must be between 0 and 50000",
                    error.exception.args[0],
                )

    def test_valid_metadata_values(self):
        """Valid metadata: proper hex, empty (removal), and the max length."""
        valid = str_to_hex(
            json.dumps(
                {"ticker": "TBILL", "name": "T-Bill", "icon": "https://ex.org/i.png"}
            )
        )
        for metadata in (valid, "", "FF" * 1024):
            with self.subTest(length=len(metadata)):
                tx = MPTokenIssuanceSet(
                    account=_ACCOUNT,
                    mptoken_issuance_id=_TOKEN_ID,
                    mptoken_metadata=metadata,
                )
                self.assertTrue(tx.is_valid())

    def test_metadata_invalid_fails(self):
        """Metadata that is too long or not valid hex is rejected."""
        cases = [
            ("FF" * 1025, "Metadata must be a hex string less than 1024 bytes"),
            ("not_hex_string", "Metadata must be a valid hex string"),
        ]
        for metadata, message in cases:
            with self.subTest(message=message):
                with self.assertRaises(XRPLModelException) as error:
                    MPTokenIssuanceSet(
                        account=_ACCOUNT,
                        mptoken_issuance_id=_TOKEN_ID,
                        mptoken_metadata=metadata,
                    )
                self.assertIn(message, error.exception.args[0])

    def test_metadata_emits_warning_for_missing_fields(self):
        """Test that warnings are emitted for metadata missing required fields."""
        invalid_metadata = {
            "ticker": "TBILL",
            "name": "T-Bill Yield Token",
            "invalid_field": "should cause warning",
        }

        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mptoken_metadata=str_to_hex(json.dumps(invalid_metadata)),
        )

        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            valid = tx.is_valid()
            self.assertTrue(valid)
            self.assertTrue(len(caught_warnings) > 0, "Expected warning not emitted")
            warning_messages = [str(w.message) for w in caught_warnings]
            found = any(
                "- icon/i: should be a non-empty string." in msg
                for msg in warning_messages
            )
            self.assertTrue(found, "- icon/i: should be a non-empty string.")
