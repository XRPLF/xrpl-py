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

# Ledger ImmutableFlags bits for MPTokenIssuance (lsif*)
LSIF_MPT_CAN_LOCK = 0x00000002
LSIF_MPT_METADATA = 0x00010000


class TestDynamicMPT(IntegrationTestCase):
    """DynamicMPT: fields/flags are mutable by default; issuers opt into
    immutability via ImmutableFlags, and enable capability flags via Flags."""

    async def _create(self, client, **kwargs):
        """Create an MPTokenIssuance and return its issuance id."""
        create_tx = MPTokenIssuanceCreate(account=WALLET.classic_address, **kwargs)
        response = await sign_and_reliable_submission_async(create_tx, WALLET, client)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        tx_hash = response.result["tx_json"]["hash"]
        tx_response = await client.request(Tx(transaction=tx_hash))
        return tx_response.result["meta"]["mpt_issuance_id"]

    async def _issuance(self, client, mpt_id):
        """Fetch the MPTokenIssuance ledger object by id."""
        response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )
        return next(
            obj
            for obj in response.result["account_objects"]
            if obj["mpt_issuance_id"] == mpt_id
        )

    @test_async_and_sync(globals())
    async def test_create_and_update_metadata(self, client):
        """Metadata is mutable by default and can be updated via Set."""
        metadata1 = {"ticker": "DMPT", "name": "v1", "icon": "https://ex.org/v1.png"}
        mpt_id = await self._create(
            client, asset_scale=2, mptoken_metadata=str_to_hex(json.dumps(metadata1))
        )

        metadata2 = {"ticker": "DMPT", "name": "v2", "icon": "https://ex.org/v2.png"}
        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mptoken_metadata=str_to_hex(json.dumps(metadata2)),
        )
        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertEqual(update_response.result["engine_result"], "tesSUCCESS")

        mpt_issuance = await self._issuance(client, mpt_id)
        self.assertEqual(
            mpt_issuance["MPTokenMetadata"].upper(),
            str_to_hex(json.dumps(metadata2)).upper(),
        )

    @test_async_and_sync(globals())
    async def test_create_and_update_transfer_fee(self, client):
        """TransferFee is mutable by default and can be updated via Set."""
        mpt_id = await self._create(
            client,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            transfer_fee=100,
        )

        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            transfer_fee=200,
        )
        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertEqual(update_response.result["engine_result"], "tesSUCCESS")

        mpt_issuance = await self._issuance(client, mpt_id)
        self.assertEqual(mpt_issuance["TransferFee"], 200)

    @test_async_and_sync(globals())
    async def test_enable_capability_flag(self, client):
        """A capability flag (in Flags) enables the corresponding lsf flag."""
        mpt_id = await self._create(client, asset_scale=2)

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK,
        )
        set_response = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(set_response.result["engine_result"], "tesSUCCESS")

        mpt_issuance = await self._issuance(client, mpt_id)
        self.assertTrue(mpt_issuance["Flags"] & LSF_MPT_CAN_LOCK)

    @test_async_and_sync(globals())
    async def test_enable_immutable_flag_fails(self, client):
        """A capability made immutable at creation can never be enabled."""
        # Make CanLock immutable at creation (it is never set, and stays unset).
        mpt_id = await self._create(
            client,
            asset_scale=2,
            immutable_flags=MPTokenIssuanceImmutableFlag.TIF_MPT_CAN_LOCK,
        )

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK,
        )
        set_response = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(set_response.result["engine_result"], "tecNO_PERMISSION")

        mpt_issuance = await self._issuance(client, mpt_id)
        # CanLock is not set, and CanLock is recorded as immutable.
        self.assertFalse(mpt_issuance["Flags"] & LSF_MPT_CAN_LOCK)
        self.assertTrue(mpt_issuance["ImmutableFlags"] & LSIF_MPT_CAN_LOCK)

    @test_async_and_sync(globals())
    async def test_reenable_capability_flag_is_noop(self, client):
        """Re-enabling an already-enabled capability flag is a valid no-op."""
        mpt_id = await self._create(client, asset_scale=2)
        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK,
        )
        first = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(first.result["engine_result"], "tesSUCCESS")
        second = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(second.result["engine_result"], "tesSUCCESS")

        mpt_issuance = await self._issuance(client, mpt_id)
        self.assertTrue(mpt_issuance["Flags"] & LSF_MPT_CAN_LOCK)

    @test_async_and_sync(globals())
    async def test_enable_multiple_capability_flags(self, client):
        """Multiple capability flags can be enabled in a single transaction."""
        mpt_id = await self._create(client, asset_scale=2)

        set_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            flags=MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_LOCK
            | MPTokenIssuanceSetFlag.TF_MPT_SET_CAN_ESCROW,
        )
        set_response = await sign_and_reliable_submission_async(set_tx, WALLET, client)
        self.assertEqual(set_response.result["engine_result"], "tesSUCCESS")

        mpt_issuance = await self._issuance(client, mpt_id)
        self.assertTrue(mpt_issuance["Flags"] & LSF_MPT_CAN_LOCK)
        self.assertTrue(mpt_issuance["Flags"] & LSF_MPT_CAN_ESCROW)

    @test_async_and_sync(globals())
    async def test_set_immutable_flag_then_field_rejected(self, client):
        """After making metadata immutable, further metadata updates are rejected."""
        metadata = {"ticker": "DMPT", "name": "v1", "icon": "https://ex.org/v1.png"}
        mpt_id = await self._create(
            client, asset_scale=2, mptoken_metadata=str_to_hex(json.dumps(metadata))
        )

        # Make MPTokenMetadata immutable.
        immut_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            immutable_flags=MPTokenIssuanceImmutableFlag.TIF_MPT_METADATA,
        )
        immut_response = await sign_and_reliable_submission_async(
            immut_tx, WALLET, client
        )
        self.assertEqual(immut_response.result["engine_result"], "tesSUCCESS")

        mpt_issuance = await self._issuance(client, mpt_id)
        self.assertTrue(mpt_issuance["ImmutableFlags"] & LSIF_MPT_METADATA)

        # A subsequent metadata update must be rejected.
        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mptoken_metadata=str_to_hex(json.dumps({"ticker": "DMPT", "name": "v2"})),
        )
        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertEqual(update_response.result["engine_result"], "tecNO_PERMISSION")

    @test_async_and_sync(globals())
    async def test_remove_metadata(self, client):
        """Setting an empty MPTokenMetadata removes the field."""
        metadata = {"ticker": "DMPT", "name": "n", "icon": "https://ex.org/d.png"}
        mpt_id = await self._create(
            client, asset_scale=2, mptoken_metadata=str_to_hex(json.dumps(metadata))
        )

        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            mptoken_metadata="",
        )
        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertEqual(update_response.result["engine_result"], "tesSUCCESS")

        mpt_issuance = await self._issuance(client, mpt_id)
        self.assertNotIn("MPTokenMetadata", mpt_issuance)

    @test_async_and_sync(globals())
    async def test_remove_transfer_fee(self, client):
        """Setting TransferFee to zero removes the field."""
        mpt_id = await self._create(
            client,
            asset_scale=2,
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            transfer_fee=100,
        )

        update_tx = MPTokenIssuanceSet(
            account=WALLET.classic_address,
            mptoken_issuance_id=mpt_id,
            transfer_fee=0,
        )
        update_response = await sign_and_reliable_submission_async(
            update_tx, WALLET, client
        )
        self.assertEqual(update_response.result["engine_result"], "tesSUCCESS")

        mpt_issuance = await self._issuance(client, mpt_id)
        self.assertNotIn("TransferFee", mpt_issuance)
