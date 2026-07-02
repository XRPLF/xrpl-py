"""Integration tests for DynamicMPT (XLS-94) feature."""

import json

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.requests.tx import Tx
from xrpl.models.transactions import (
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
    MPTokenIssuanceCreateMutableFlag,
    MPTokenIssuanceSet,
    MPTokenIssuanceSetMutableFlag,
)
from xrpl.utils import str_to_hex

# Ledger flag constants for MPTokenIssuance
LSF_MPT_CAN_LOCK = 0x00000002
LSF_MPT_REQUIRE_AUTH = 0x00000004
LSF_MPT_CAN_ESCROW = 0x00000008
LSF_MPT_CAN_TRADE = 0x00000010
LSF_MPT_CAN_TRANSFER = 0x00000020
LSF_MPT_CAN_CLAWBACK = 0x00000040


class TestDynamicMPT(IntegrationTestCase):
    """Test DynamicMPT functionality including mutable fields and flags."""

    @test_async_and_sync(globals())
    async def test_create_with_mutable_metadata(self, client):
        """Test creating MPT with mutable metadata flag."""
        metadata = {
            "ticker": "DMPT",
            "name": "Dynamic MPT",
            "icon": "https://example.org/dmpt.png",
        }

        tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            mptoken_metadata=str_to_hex(json.dumps(metadata)),
            mutable_flags=MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_MUTATE_METADATA,
        )

        response = await sign_and_reliable_submission_async(tx, WALLET, client)

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Get the MPTokenIssuanceID using Tx request
        tx_hash = response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Verify MPTokenIssuance was created with correct metadata
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        self.assertTrue(len(account_objects_response.result["account_objects"]) > 0)

        # Find the created MPTokenIssuance object
        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )

        # Verify metadata was set correctly
        # (compare uppercase to handle hex case differences)
        self.assertEqual(
            mpt_issuance["MPTokenMetadata"].upper(),
            str_to_hex(json.dumps(metadata)).upper(),
        )

    @test_async_and_sync(globals())
    async def test_create_with_mutable_transfer_fee(self, client):
        """Test creating MPT with mutable transfer fee flag."""
        tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            transfer_fee=100,
            mutable_flags=(
                MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_MUTATE_TRANSFER_FEE
            ),
        )

        response = await sign_and_reliable_submission_async(tx, WALLET, client)

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Get the MPTokenIssuanceID using Tx request
        tx_hash = response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Verify transfer fee was set correctly
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )

        # Verify TransferFee field was set
        self.assertEqual(mpt_issuance["TransferFee"], 100)

    @test_async_and_sync(globals())
    async def test_update_metadata(self, client):
        """Test updating metadata on an MPT with mutable metadata."""
        # Create MPT with mutable metadata
        metadata1 = {
            "ticker": "DMPT",
            "name": "Dynamic MPT v1",
            "icon": "https://example.org/v1.png",
        }

        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            mptoken_metadata=str_to_hex(json.dumps(metadata1)),
            mutable_flags=MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_MUTATE_METADATA,
        )

        create_response = await sign_and_reliable_submission_async(
            create_tx, WALLET, client
        )
        self.assertTrue(create_response.is_successful())

        # Get the MPTokenIssuanceID using Tx request
        tx_hash = create_response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Update metadata
        metadata2 = {
            "ticker": "DMPT",
            "name": "Dynamic MPT v2",
            "icon": "https://example.org/v2.png",
        }

        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mptoken_metadata=str_to_hex(json.dumps(metadata2)),
        )

        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertTrue(update_response.is_successful())
        self.assertEqual(update_response.result["engine_result"], "tesSUCCESS")

        # Verify metadata was actually updated on the ledger
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )

        # Verify the metadata field was updated to metadata2
        self.assertEqual(
            mpt_issuance["MPTokenMetadata"].upper(),
            str_to_hex(json.dumps(metadata2)).upper(),
        )

    @test_async_and_sync(globals())
    async def test_update_transfer_fee(self, client):
        """Test updating transfer fee on an MPT."""
        # Create MPT with mutable transfer fee
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            transfer_fee=100,
            mutable_flags=(
                MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_MUTATE_TRANSFER_FEE
            ),
        )

        create_response = await sign_and_reliable_submission_async(
            create_tx, WALLET, client
        )
        self.assertTrue(create_response.is_successful())

        # Get the MPTokenIssuanceID using Tx request
        tx_hash = create_response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Update transfer fee
        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            transfer_fee=200,
        )

        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertTrue(update_response.is_successful())
        self.assertEqual(update_response.result["engine_result"], "tesSUCCESS")

        # Verify transfer fee was actually updated on the ledger
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )

        # Verify the TransferFee field was updated to 200
        self.assertEqual(mpt_issuance["TransferFee"], 200)

    @test_async_and_sync(globals())
    async def test_enable_flag(self, client):
        """Test enabling a mutable flag (one-way: cannot be disabled afterward)."""
        # Create MPT with mutable CAN_LOCK flag
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            mutable_flags=MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_ENABLE_CAN_LOCK,
        )

        create_response = await sign_and_reliable_submission_async(
            create_tx, WALLET, client
        )
        self.assertTrue(create_response.is_successful())

        # Get the MPTokenIssuanceID using Tx request
        tx_hash = create_response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Set CAN_LOCK flag
        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK,
        )

        set_response = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertTrue(set_response.is_successful())
        self.assertEqual(set_response.result["engine_result"], "tesSUCCESS")

        # Verify CAN_LOCK flag was set on the ledger
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )

        # Verify lsfMPTCanLock flag is set
        self.assertTrue(mpt_issuance["Flags"] & LSF_MPT_CAN_LOCK)

    @test_async_and_sync(globals())
    async def test_enable_flag_not_declared_mutable_fails(self, client):
        """A flag not declared mutable at creation cannot be enabled later.

        This enforces the one-way model: since clear flags no longer exist, the
        only control over a flag is enabling one that was declared mutable. A
        flag that was never declared mutable can never be turned on.
        """
        # Create MPT declaring only CAN_ESCROW mutable (CAN_LOCK is NOT mutable)
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            mutable_flags=(
                MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_ENABLE_CAN_ESCROW
            ),
        )

        create_response = await sign_and_reliable_submission_async(
            create_tx, WALLET, client
        )
        self.assertTrue(create_response.is_successful())

        # Get the MPTokenIssuanceID using Tx request
        tx_hash = create_response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Attempt to enable CAN_LOCK, which was not declared mutable
        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK,
        )

        set_response = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(set_response.result["engine_result"], "tecNO_PERMISSION")

        # Verify lsfMPTCanLock flag was NOT set on the ledger
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )
        self.assertFalse(mpt_issuance["Flags"] & LSF_MPT_CAN_LOCK)

    @test_async_and_sync(globals())
    async def test_reenable_already_enabled_flag_is_noop(self, client):
        """Re-enabling an already-enabled flag succeeds with no additional effect.

        Per XLS-94, enabling a mutable flag is one-way and idempotent: once the
        flag is on, re-issuing the same enable is valid (tesSUCCESS) and leaves
        the flag set.
        """
        # Create MPT declaring CAN_LOCK mutable
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            mutable_flags=MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_ENABLE_CAN_LOCK,
        )
        create_response = await sign_and_reliable_submission_async(
            create_tx, WALLET, client
        )
        self.assertTrue(create_response.is_successful())

        tx_hash = create_response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Enable CAN_LOCK
        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mutable_flags=MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK,
        )
        first_response = await sign_and_reliable_submission_async(
            set_tx, WALLET, client
        )
        self.assertEqual(first_response.result["engine_result"], "tesSUCCESS")

        # Enable CAN_LOCK again - idempotent, still succeeds
        second_response = await sign_and_reliable_submission_async(
            set_tx, WALLET, client
        )
        self.assertEqual(second_response.result["engine_result"], "tesSUCCESS")

        # Verify lsfMPTCanLock flag is still set
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )
        self.assertTrue(mpt_issuance["Flags"] & LSF_MPT_CAN_LOCK)

    @test_async_and_sync(globals())
    async def test_multiple_mutable_flags(self, client):
        """Test setting multiple mutable flags simultaneously."""
        # Create MPT with multiple mutable flags
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            mutable_flags=(
                MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_ENABLE_CAN_LOCK
                | MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_ENABLE_CAN_ESCROW
                | MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_MUTATE_TRANSFER_FEE
            ),
        )

        create_response = await sign_and_reliable_submission_async(
            create_tx, WALLET, client
        )
        self.assertTrue(create_response.is_successful())

        # Get the MPTokenIssuanceID using Tx request
        tx_hash = create_response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Set multiple flags and transfer fee
        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mutable_flags=(
                MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_LOCK
                | MPTokenIssuanceSetMutableFlag.TMF_MPT_SET_CAN_ESCROW
            ),
            transfer_fee=150,
        )

        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertTrue(update_response.is_successful())
        self.assertEqual(update_response.result["engine_result"], "tesSUCCESS")

        # Verify flags and transfer fee were updated on the ledger
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )

        # Verify CAN_LOCK flag is set
        self.assertTrue(mpt_issuance["Flags"] & LSF_MPT_CAN_LOCK)

        # Verify CAN_ESCROW flag is set
        self.assertTrue(mpt_issuance["Flags"] & LSF_MPT_CAN_ESCROW)

        # Verify TransferFee was set to 150
        self.assertEqual(mpt_issuance["TransferFee"], 150)

    @test_async_and_sync(globals())
    async def test_remove_metadata(self, client):
        """Test removing metadata by setting empty string."""
        # Create MPT with metadata
        metadata = {
            "ticker": "DMPT",
            "name": "Dynamic MPT",
            "icon": "https://example.org/dmpt.png",
        }

        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            mptoken_metadata=str_to_hex(json.dumps(metadata)),
            mutable_flags=MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_MUTATE_METADATA,
        )

        create_response = await sign_and_reliable_submission_async(
            create_tx, WALLET, client
        )
        self.assertTrue(create_response.is_successful())

        # Get the MPTokenIssuanceID using Tx request
        tx_hash = create_response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Remove metadata with empty string
        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mptoken_metadata="",
        )

        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertTrue(update_response.is_successful())
        self.assertEqual(update_response.result["engine_result"], "tesSUCCESS")

        # Verify metadata was removed from the ledger
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )

        # Verify MPTokenMetadata field is absent
        self.assertNotIn("MPTokenMetadata", mpt_issuance)

    @test_async_and_sync(globals())
    async def test_remove_transfer_fee(self, client):
        """Test removing transfer fee by setting it to zero."""
        # Create MPT with transfer fee
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            transfer_fee=100,
            mutable_flags=(
                MPTokenIssuanceCreateMutableFlag.TMF_MPT_CAN_MUTATE_TRANSFER_FEE
            ),
        )

        create_response = await sign_and_reliable_submission_async(
            create_tx, WALLET, client
        )
        self.assertTrue(create_response.is_successful())

        # Get the MPTokenIssuanceID using Tx request
        tx_hash = create_response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        mpt_id = tx_response.result["meta"]["mpt_issuance_id"]

        # Remove transfer fee by setting to zero
        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            transfer_fee=0,
        )

        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertTrue(update_response.is_successful())
        self.assertEqual(update_response.result["engine_result"], "tesSUCCESS")

        # Verify transfer fee was removed from the ledger
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        mpt_issuance = next(
            obj
            for obj in account_objects_response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )

        # Verify TransferFee field is absent
        self.assertNotIn("TransferFee", mpt_issuance)
