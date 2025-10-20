import json
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
    def test_tx_is_valid(self):
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_holder(self):
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
            flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_without_flags(self):
        # It's fine to not specify any flag, it means only tx fee is deducted
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_flag_conflict(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
                flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK
                | MPTokenIssuanceSetFlag.TF_MPT_UNLOCK,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'flags': \"flag conflict: both TF_MPT_LOCK and TF_MPT_UNLOCK can't be set"
            '"}',
        )

    # DynamicMPT tests
    def test_tx_with_mptoken_metadata(self):
        metadata = {"ticker": "TBILL", "name": "T-Bill", "icon": "https://ex.org/i.png"}
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mptoken_metadata=str_to_hex(json.dumps(metadata)),
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_empty_mptoken_metadata(self):
        # Empty string removes the metadata field
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mptoken_metadata="",
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_transfer_fee(self):
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            transfer_fee=200,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_zero_transfer_fee(self):
        # Zero removes the transfer_fee field
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            transfer_fee=0,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_mutable_flags_set_can_lock(self):
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_mutable_flags_clear_can_lock(self):
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_LOCK,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_multiple_mutable_flags(self):
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK
            | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_ESCROW,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_mutable_flags_and_transfer_fee(self):
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK,
            transfer_fee=200,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_holder_with_dynamic_fields_fails(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
                mptoken_metadata="464F4F",
            )
        self.assertIn("holder cannot be provided", error.exception.args[0])

    def test_tx_flags_with_dynamic_fields_fails(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
                mptoken_metadata="464F4F",
            )
        self.assertIn("Flags cannot be provided when", error.exception.args[0])

    def test_tx_mutable_flags_zero_fails(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=0,
            )
        self.assertIn("mutable_flags cannot be 0", error.exception.args[0])

    def test_tx_mutable_flags_conflict_can_lock(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_CAN_LOCK,
            )
        self.assertIn("Cannot set and clear CAN_LOCK", error.exception.args[0])

    def test_tx_mutable_flags_conflict_require_auth(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_REQUIRE_AUTH
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_CLEAR_REQUIRE_AUTH,
            )
        self.assertIn("Cannot set and clear REQUIRE_AUTH", error.exception.args[0])

    def test_tx_transfer_fee_with_clear_can_transfer_fails(self):
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

    def test_tx_transfer_fee_out_of_range(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                transfer_fee=50001,
            )
        self.assertIn(
            "transfer_fee must be between 0 and 50000", error.exception.args[0]
        )

    def test_tx_mptoken_metadata_too_long(self):
        # Create a hex string longer than 2048 characters (1024 bytes)
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

    def test_tx_mptoken_metadata_not_hex(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                mptoken_metadata="not_hex_string",
            )
        self.assertIn("Metadata must be a valid hex string", error.exception.args[0])
