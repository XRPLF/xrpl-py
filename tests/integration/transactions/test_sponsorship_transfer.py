"""Integration tests for SponsorshipTransfer transaction type (XLS-68)."""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models import (
    AccountObjects,
    AccountObjectType,
    SponsorshipSet,
    SponsorshipTransfer,
)
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.sponsorship_transfer import SponsorshipTransferFlag
from xrpl.wallet import Wallet


class TestSponsorshipTransfer(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_sponsorship_transfer(self, client):
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        new_sponsor_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(new_sponsor_wallet)

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

        # Retrieve the Sponsorship object ID from the created objects
        account_objects_response = await client.request(
            AccountObjects(
                account=sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        self.assertTrue(len(account_objects_response.result["account_objects"]) > 0)
        sponsorship_object = account_objects_response.result["account_objects"][0]
        object_id = sponsorship_object["index"]

        # Transfer the sponsorship to the new sponsor
        transfer_tx = SponsorshipTransfer(
            account=new_sponsor_wallet.address,
            object_id=object_id,
            sponsee=sponsee_wallet.address,
            flags=SponsorshipTransferFlag.TF_SPONSORSHIP_REASSIGN,
        )
        transfer_response = await sign_and_reliable_submission_async(
            transfer_tx, new_sponsor_wallet, client
        )
        self.assertEqual(transfer_response.status, ResponseStatus.SUCCESS)
        self.assertEqual(transfer_response.result["engine_result"], "tesSUCCESS")

        # Confirm the new sponsor now owns the Sponsorship object
        new_sponsor_objects_response = await client.request(
            AccountObjects(
                account=new_sponsor_wallet.address,
                type=AccountObjectType.SPONSORSHIP,
            )
        )
        self.assertTrue(len(new_sponsor_objects_response.result["account_objects"]) > 0)

        # TODO: Confirm that the old sponsor does not have the transferred Object.


# TODO: Add integration tests that cover two other cases of sponsorship transfer.
