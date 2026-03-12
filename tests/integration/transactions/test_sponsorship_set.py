"""Integration tests for SponsorshipSet transaction type (XLS-68)."""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models import AccountObjects, AccountObjectType, SponsorshipSet
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.sponsorship_set import SponsorshipSetFlag
from xrpl.wallet import Wallet


# CK TODO: Write integration tests that include all potential fields of the SponsorshipSet transaction and associated flags
class TestSponsorshipSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_sponsorship_set(self, client):
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
        )
        response = await sign_and_reliable_submission_async(tx, sponsor_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Confirm that the Sponsorship object was created
        account_objects_response = await client.request(
            AccountObjects(
                account=sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        self.assertTrue(len(account_objects_response.result["account_objects"]) > 0)

    @test_async_and_sync(globals())
    async def test_sponsorship_set_with_fee_amount(self, client):
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            fee_amount="1000000",
        )
        response = await sign_and_reliable_submission_async(tx, sponsor_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Confirm that the Sponsorship object was created
        account_objects_response = await client.request(
            AccountObjects(
                account=sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        self.assertTrue(len(account_objects_response.result["account_objects"]) > 0)

    @test_async_and_sync(globals())
    async def test_sponsorship_set_delete(self, client):
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        # First, create a sponsorship
        create_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
        )
        create_response = await sign_and_reliable_submission_async(
            create_tx, sponsor_wallet, client
        )
        self.assertEqual(create_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(create_response.result["engine_result"], "tesSUCCESS")

        # Then, delete the sponsorship using TF_DELETE_OBJECT flag
        delete_tx = SponsorshipSet(
            account=sponsor_wallet.address,
            sponsee=sponsee_wallet.address,
            flags=SponsorshipSetFlag.TF_DELETE_OBJECT,
        )
        delete_response = await sign_and_reliable_submission_async(
            delete_tx, sponsor_wallet, client
        )
        self.assertEqual(delete_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(delete_response.result["engine_result"], "tesSUCCESS")

        # Confirm that the Sponsorship object was deleted
        account_objects_response = await client.request(
            AccountObjects(
                account=sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 0)
