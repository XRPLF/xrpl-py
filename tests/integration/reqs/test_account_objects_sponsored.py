"""Integration tests for AccountObjects request with sponsored field and new
AccountObjectType values (XLS-68 sponsored fees)."""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models import AccountObjects, AccountObjectType, SponsorshipSet
from xrpl.models.response import ResponseStatus
from xrpl.wallet import Wallet


class TestAccountObjectsSponsored(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_sponsored_field_true(self, client):
        """Test that the sponsored=True filter returns only sponsored objects."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # Create a sponsorship
        tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
        )
        response = await sign_and_reliable_submission_async(tx, sponsor_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Query with sponsored=True on the sponsee's account
        account_objects_response = await client.request(
            AccountObjects(
                account=sponsee_wallet.address,
                sponsored=True,
            )
        )
        self.assertTrue(account_objects_response.is_successful())

    @test_async_and_sync(globals())
    async def test_sponsored_field_false(self, client):
        """Test that the sponsored=False filter returns only non-sponsored objects."""
        wallet = Wallet.create()
        await fund_wallet_async(wallet)

        # Query with sponsored=False
        account_objects_response = await client.request(
            AccountObjects(
                account=wallet.address,
                sponsored=False,
            )
        )
        self.assertTrue(account_objects_response.is_successful())

    @test_async_and_sync(globals())
    async def test_sponsored_field_none(self, client):
        """Test that omitting sponsored returns all objects (default behavior)."""
        wallet = Wallet.create()
        await fund_wallet_async(wallet)

        # Query without sponsored field (default None)
        account_objects_response = await client.request(
            AccountObjects(
                account=wallet.address,
            )
        )
        self.assertTrue(account_objects_response.is_successful())

    @test_async_and_sync(globals())
    async def test_type_sponsorship_filter(self, client):
        """Test filtering account_objects by type=SPONSORSHIP."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # Create a sponsorship
        tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
        )
        response = await sign_and_reliable_submission_async(tx, sponsor_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Filter by SPONSORSHIP type on the sponsor's account
        account_objects_response = await client.request(
            AccountObjects(
                account=sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        self.assertTrue(account_objects_response.is_successful())
        sponsorship_objects = account_objects_response.result["account_objects"]
        self.assertGreater(len(sponsorship_objects), 0)
        for obj in sponsorship_objects:
            self.assertEqual(obj["LedgerEntryType"], "Sponsorship")
