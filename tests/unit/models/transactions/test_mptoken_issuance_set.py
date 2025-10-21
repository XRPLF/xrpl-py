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
            | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_ESCROW,
            transfer_fee=200,
            mptoken_metadata=str_to_hex(json.dumps(metadata)),
        )
        self.assertTrue(tx.is_valid())

    def test_holder_with_mutable_flags_fails(self):
        """Test that holder cannot be provided with mutable_flags."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK,
            )
        self.assertIn("holder cannot be provided", error.exception.args[0])

    def test_holder_with_metadata_fails(self):
        """Test that holder cannot be provided with mptoken_metadata."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
                mptoken_metadata="464F4F",
            )
        self.assertIn("holder cannot be provided", error.exception.args[0])

    def test_holder_with_transfer_fee_fails(self):
        """Test that holder cannot be provided with transfer_fee."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
                transfer_fee=200,
            )
        self.assertIn("holder cannot be provided", error.exception.args[0])

    def test_flags_with_mutable_flags_fails(self):
        """Test that Flags cannot be provided with mutable_flags."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK,
            )
        self.assertIn("Flags cannot be provided when", error.exception.args[0])

    def test_flags_with_metadata_fails(self):
        """Test that Flags cannot be provided with mptoken_metadata."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
                mptoken_metadata="464F4F",
            )
        self.assertIn("Flags cannot be provided when", error.exception.args[0])

    def test_flags_with_transfer_fee_fails(self):
        """Test that Flags cannot be provided with transfer_fee."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
                transfer_fee=200,
            )
        self.assertIn("Flags cannot be provided when", error.exception.args[0])

    def test_mutable_flags_zero_fails(self):
        """Test that mutable_flags cannot be 0."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=0,
            )
        self.assertIn("mutable_flags cannot be 0", error.exception.args[0])

    def test_mutable_flags_invalid_bits(self):
        """Test that invalid/reserved bits are rejected."""
        invalid_flag = 0x00001000  # Bit 12 is not defined
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=invalid_flag,
            )
        self.assertIn(
            "mutable_flags contains invalid bits",
            error.exception.args[0],
        )

    def test_mutable_flags_mixed_valid_and_invalid_bits(self):
        """Test that mixing valid and invalid bits is rejected."""
        mixed_flags = (
            MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK.value | 0x00010000
        )
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=mixed_flags,
            )
        self.assertIn(
            "mutable_flags contains invalid bits",
            error.exception.args[0],
        )

    def test_mutable_flags_set_clear_can_lock_conflict(self):
        """Test that SET and CLEAR CAN_LOCK cannot both be set."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_LOCK,
            )
        self.assertIn("Cannot set and clear CAN_LOCK", error.exception.args[0])

    def test_mutable_flags_set_clear_require_auth_conflict(self):
        """Test that SET and CLEAR REQUIRE_AUTH cannot both be set."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_REQUIRE_AUTH
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_REQUIRE_AUTH,
            )
        self.assertIn("Cannot set and clear REQUIRE_AUTH", error.exception.args[0])

    def test_mutable_flags_set_clear_can_escrow_conflict(self):
        """Test that SET and CLEAR CAN_ESCROW cannot both be set."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_ESCROW
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_ESCROW,
            )
        self.assertIn("Cannot set and clear CAN_ESCROW", error.exception.args[0])

    def test_mutable_flags_set_clear_can_trade_conflict(self):
        """Test that SET and CLEAR CAN_TRADE cannot both be set."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_TRADE
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_TRADE,
            )
        self.assertIn("Cannot set and clear CAN_TRADE", error.exception.args[0])

    def test_mutable_flags_set_clear_can_transfer_conflict(self):
        """Test that SET and CLEAR CAN_TRANSFER cannot both be set."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_TRANSFER
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_TRANSFER,
            )
        self.assertIn("Cannot set and clear CAN_TRANSFER", error.exception.args[0])

    def test_mutable_flags_set_clear_can_clawback_conflict(self):
        """Test that SET and CLEAR CAN_CLAWBACK cannot both be set."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_CLAWBACK
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_CLAWBACK,
            )
        self.assertIn("Cannot set and clear CAN_CLAWBACK", error.exception.args[0])

    def test_transfer_fee_with_clear_can_transfer_fails(self):
        """Test that non-zero transfer_fee cannot be set when clearing CAN_TRANSFER."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                transfer_fee=200,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_TRANSFER,
            )
        self.assertIn(
            "Cannot include non-zero transfer_fee when clearing CAN_TRANSFER",
            error.exception.args[0],
        )

    def test_zero_transfer_fee_with_clear_can_transfer_valid(self):
        """Test that zero transfer_fee is allowed when clearing CAN_TRANSFER."""
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            transfer_fee=0,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_TRANSFER,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_transfer_fee(self):
        """Test valid transaction with transfer fee."""
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            transfer_fee=200,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_zero_transfer_fee(self):
        """Test valid transaction with zero transfer fee (removes field)."""
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            transfer_fee=0,
        )
        self.assertTrue(tx.is_valid())

    def test_transfer_fee_negative_fails(self):
        """Test that negative transfer_fee is rejected."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                transfer_fee=-1,
            )
        self.assertIn(
            "transfer_fee must be between 0 and 50000", error.exception.args[0]
        )

    def test_transfer_fee_exceeds_max_fails(self):
        """Test that transfer_fee > 50000 is rejected."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                transfer_fee=50001,
            )
        self.assertIn(
            "transfer_fee must be between 0 and 50000", error.exception.args[0]
        )

    def test_transfer_fee_at_max_valid(self):
        """Test that transfer_fee = 50000 is valid."""
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            transfer_fee=50000,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_metadata(self):
        """Test valid transaction with metadata."""
        metadata = {"ticker": "TBILL", "name": "T-Bill", "icon": "https://ex.org/i.png"}
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mptoken_metadata=str_to_hex(json.dumps(metadata)),
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_empty_metadata(self):
        """Test valid transaction with empty metadata (removes field)."""
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mptoken_metadata="",
        )
        self.assertTrue(tx.is_valid())

    def test_metadata_too_long_fails(self):
        """Test that metadata > 1024 bytes is rejected."""
        long_metadata = "FF" * 1025
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mptoken_metadata=long_metadata,
            )
        self.assertIn(
            "Metadata must be a hex string less than 1024 bytes",
            error.exception.args[0],
        )

    def test_metadata_at_max_length_valid(self):
        """Test that metadata = 1024 bytes (2048 hex chars) is valid."""
        max_metadata = "FF" * 1024
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mptoken_metadata=max_metadata,
        )
        self.assertTrue(tx.is_valid())

    def test_metadata_not_hex_fails(self):
        """Test that non-hex metadata is rejected."""
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mptoken_metadata="not_hex_string",
            )
        self.assertIn("Metadata must be a valid hex string", error.exception.args[0])

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
                "- icon is required and must be string." in msg
                for msg in warning_messages
            )
            self.assertTrue(found, "- icon is required and must be string.")
