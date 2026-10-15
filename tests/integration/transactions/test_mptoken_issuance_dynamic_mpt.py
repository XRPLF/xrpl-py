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
    MPTokenIssuanceImmutableFlag,
    MPTokenIssuanceSet,
    MPTokenIssuanceSetFlag,
)
from xrpl.utils import str_to_hex

# Ledger Flags bits for MPTokenIssuance
LSF_MPT_CAN_LOCK = 0x00000002
LSF_MPT_CAN_ESCROW = 0x00000008
LSF_MPT_CAN_TRANSFER = 0x00000020

# Ledger ImmutableFlags bits for MPTokenIssuance (lsif*)
LSIF_MPT_CAN_LOCK = 0x00000002
LSIF_MPT_METADATA = 0x00010000
LSIF_MPT_TRANSFER_FEE = 0x00020000


class TestDynamicMPT(IntegrationTestCase):
    """DynamicMPT: fields/flags are mutable by default; issuers opt into
    immutability via ImmutableFlags, and enable capability flags via Flags."""

    # --- Mutable by default ---
    @test_async_and_sync(globals())
    async def test_create_and_update_metadata(self, client):
        """Metadata is mutable by default and can be updated via Set."""
        metadata1 = {"ticker": "DMPT", "name": "v1", "icon": "https://ex.org/v1.png"}
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            mptoken_metadata=str_to_hex(json.dumps(metadata1)),
        )
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        metadata2 = {"ticker": "DMPT", "name": "v2", "icon": "https://ex.org/v2.png"}
        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mptoken_metadata=str_to_hex(json.dumps(metadata2)),
        )
        update_res = await sign_and_reliable_submission_async(update_tx, WALLET, client)
        self.assertEqual(update_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertEqual(
            issuance["MPTokenMetadata"].upper(),
            str_to_hex(json.dumps(metadata2)).upper(),
        )

    @test_async_and_sync(globals())
    async def test_create_and_update_transfer_fee(self, client):
        """TransferFee is mutable by default and can be updated via Set."""
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            transfer_fee=100,
        )
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            transfer_fee=200,
        )
        update_res = await sign_and_reliable_submission_async(update_tx, WALLET, client)
        self.assertEqual(update_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertEqual(issuance["TransferFee"], 200)

    # --- Enable capabilities (Flags) ---
    @test_async_and_sync(globals())
    async def test_enable_capability_flag(self, client):
        """A capability flag (in Flags) enables the corresponding lsf flag."""
        create_tx = MPTokenIssuanceCreate(account=WALLET.classic_address, asset_scale=2)
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK,
        )
        set_res = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(set_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertTrue(issuance["Flags"] & LSF_MPT_CAN_LOCK)

    @test_async_and_sync(globals())
    async def test_enable_multiple_capability_flags(self, client):
        """Multiple capability flags can be enabled in a single transaction."""
        create_tx = MPTokenIssuanceCreate(account=WALLET.classic_address, asset_scale=2)
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK
            | MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_ESCROW,
        )
        set_res = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(set_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertTrue(issuance["Flags"] & LSF_MPT_CAN_LOCK)
        self.assertTrue(issuance["Flags"] & LSF_MPT_CAN_ESCROW)

    @test_async_and_sync(globals())
    async def test_reenable_capability_flag_is_noop(self, client):
        """Re-enabling an already-enabled capability flag is a valid no-op."""
        create_tx = MPTokenIssuanceCreate(account=WALLET.classic_address, asset_scale=2)
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK,
        )
        first = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(first.result["engine_result"], "tesSUCCESS")
        second = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(second.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertTrue(issuance["Flags"] & LSF_MPT_CAN_LOCK)

    # --- Immutability (ImmutableFlags) ---
    @test_async_and_sync(globals())
    async def test_enable_immutable_flag_fails(self, client):
        """A capability made immutable at creation can never be enabled."""
        # Make CanLock immutable at creation (it is never set, and stays unset).
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            immutable_flags=MPTokenIssuanceImmutableFlag.TIF_MPT_CAN_LOCK,
        )
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK,
        )
        set_res = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(set_res.result["engine_result"], "tecNO_PERMISSION")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        # CanLock is not set, and CanLock is recorded as immutable.
        self.assertFalse(issuance["Flags"] & LSF_MPT_CAN_LOCK)
        self.assertTrue(issuance["ImmutableFlags"] & LSIF_MPT_CAN_LOCK)

    @test_async_and_sync(globals())
    async def test_freeze_capability_via_set_then_enable_fails(self, client):
        """A capability frozen (while off) via Set can never be enabled."""
        create_tx = MPTokenIssuanceCreate(account=WALLET.classic_address, asset_scale=2)
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        # Freeze CanLock while it is still off.
        freeze_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            immutable_flags=MPTokenIssuanceImmutableFlag.TIF_MPT_CAN_LOCK,
        )
        freeze_res = await sign_and_reliable_submission_async(freeze_tx, WALLET, client)
        self.assertEqual(freeze_res.result["engine_result"], "tesSUCCESS")

        # Enabling the now-immutable capability must be rejected.
        enable_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK,
        )
        enable_res = await sign_and_reliable_submission_async(enable_tx, WALLET, client)
        self.assertEqual(enable_res.result["engine_result"], "tecNO_PERMISSION")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertFalse(issuance["Flags"] & LSF_MPT_CAN_LOCK)
        self.assertTrue(issuance["ImmutableFlags"] & LSIF_MPT_CAN_LOCK)

    @test_async_and_sync(globals())
    async def test_set_immutable_metadata_then_update_fails(self, client):
        """After making metadata immutable, further metadata updates are rejected."""
        metadata = {"ticker": "DMPT", "name": "v1", "icon": "https://ex.org/v1.png"}
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            mptoken_metadata=str_to_hex(json.dumps(metadata)),
        )
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        # Make MPTokenMetadata immutable.
        immut_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            immutable_flags=MPTokenIssuanceImmutableFlag.TIF_MPT_METADATA,
        )
        immut_res = await sign_and_reliable_submission_async(immut_tx, WALLET, client)
        self.assertEqual(immut_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertTrue(issuance["ImmutableFlags"] & LSIF_MPT_METADATA)

        # A subsequent metadata update must be rejected.
        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mptoken_metadata=str_to_hex(json.dumps({"ticker": "DMPT", "name": "v2"})),
        )
        update_res = await sign_and_reliable_submission_async(update_tx, WALLET, client)
        self.assertEqual(update_res.result["engine_result"], "tecNO_PERMISSION")

    @test_async_and_sync(globals())
    async def test_set_immutable_transfer_fee_then_update_fails(self, client):
        """After making TransferFee immutable, further fee updates are rejected."""
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            transfer_fee=100,
        )
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        # Make TransferFee immutable.
        immut_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            immutable_flags=MPTokenIssuanceImmutableFlag.TIF_MPT_TRANSFER_FEE,
        )
        immut_res = await sign_and_reliable_submission_async(immut_tx, WALLET, client)
        self.assertEqual(immut_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertTrue(issuance["ImmutableFlags"] & LSIF_MPT_TRANSFER_FEE)

        # A subsequent transfer_fee update must be rejected.
        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            transfer_fee=200,
        )
        update_res = await sign_and_reliable_submission_async(update_tx, WALLET, client)
        self.assertEqual(update_res.result["engine_result"], "tecNO_PERMISSION")

    @test_async_and_sync(globals())
    async def test_immutable_flags_accumulate(self, client):
        """ImmutableFlags set across separate Sets accumulate (bits are added)."""
        metadata = {"ticker": "DMPT", "name": "v1", "icon": "https://ex.org/v1.png"}
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            transfer_fee=100,
            mptoken_metadata=str_to_hex(json.dumps(metadata)),
        )
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        # First freeze: metadata.
        freeze1 = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            immutable_flags=MPTokenIssuanceImmutableFlag.TIF_MPT_METADATA,
        )
        freeze1_res = await sign_and_reliable_submission_async(freeze1, WALLET, client)
        self.assertEqual(freeze1_res.result["engine_result"], "tesSUCCESS")

        # Second freeze: transfer_fee. Should add to (not replace) the first.
        freeze2 = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            immutable_flags=MPTokenIssuanceImmutableFlag.TIF_MPT_TRANSFER_FEE,
        )
        freeze2_res = await sign_and_reliable_submission_async(freeze2, WALLET, client)
        self.assertEqual(freeze2_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        # Both bits are present.
        self.assertTrue(issuance["ImmutableFlags"] & LSIF_MPT_METADATA)
        self.assertTrue(issuance["ImmutableFlags"] & LSIF_MPT_TRANSFER_FEE)

    # --- TransferFee <-> CanTransfer interaction ---
    @test_async_and_sync(globals())
    async def test_transfer_fee_without_can_transfer_fails(self, client):
        """A non-zero fee is rejected when CanTransfer is off and not being set."""
        create_tx = MPTokenIssuanceCreate(account=WALLET.classic_address, asset_scale=2)
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            transfer_fee=200,
        )
        set_res = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(set_res.result["engine_result"], "tecNO_PERMISSION")

    @test_async_and_sync(globals())
    async def test_transfer_fee_with_enable_transfer_succeeds(self, client):
        """A non-zero fee is allowed when the same tx also enables CanTransfer."""
        create_tx = MPTokenIssuanceCreate(account=WALLET.classic_address, asset_scale=2)
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_TRANSFER,
            transfer_fee=200,
        )
        set_res = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(set_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertTrue(issuance["Flags"] & LSF_MPT_CAN_TRANSFER)
        self.assertEqual(issuance["TransferFee"], 200)

    # --- Removal ---
    @test_async_and_sync(globals())
    async def test_remove_metadata(self, client):
        """Setting an empty MPTokenMetadata removes the field."""
        metadata = {"ticker": "DMPT", "name": "n", "icon": "https://ex.org/d.png"}
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            mptoken_metadata=str_to_hex(json.dumps(metadata)),
        )
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mptoken_metadata="",
        )
        update_res = await sign_and_reliable_submission_async(update_tx, WALLET, client)
        self.assertEqual(update_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertNotIn("MPTokenMetadata", issuance)

    @test_async_and_sync(globals())
    async def test_remove_transfer_fee(self, client):
        """Setting TransferFee to zero removes the field."""
        create_tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            transfer_fee=100,
        )
        create_res = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(create_res.result["engine_result"], "tesSUCCESS")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            transfer_fee=0,
        )
        update_res = await sign_and_reliable_submission_async(update_tx, WALLET, client)
        self.assertEqual(update_res.result["engine_result"], "tesSUCCESS")

        objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        issuance = next(
            o
            for o in objects.result["account_objects"]
            if o["mpt_issuance_id"] == mpt_id
        )
        self.assertNotIn("TransferFee", issuance)
