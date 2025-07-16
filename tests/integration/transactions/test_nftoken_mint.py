from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models import AccountObjects, AccountObjectType, NFTokenMint
from xrpl.models.response import ResponseStatus
from xrpl.utils import str_to_hex
from xrpl.wallet import Wallet


class TestNFTokenMint(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        nftoken_owner_wallet = Wallet.create()
        nftoken_destination_wallet = Wallet.create()
        await fund_wallet_async(nftoken_owner_wallet)
        await fund_wallet_async(nftoken_destination_wallet)
        tx = NFTokenMint(
            account=nftoken_owner_wallet.address,
            nftoken_taxon=1,
            uri=str_to_hex("https://example.com/nftoken"),
            amount="10000",
            destination=nftoken_destination_wallet.address,
            expiration=970000000,
        )
        response = await sign_and_reliable_submission_async(
            tx, nftoken_owner_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm that the NFTokenPage was actually created
        account_objects_response = await client.request(
            AccountObjects(
                account=nftoken_owner_wallet.address, type=AccountObjectType.NFT_PAGE
            )
        )
        self.assertTrue(len(account_objects_response.result["account_objects"]) > 0)

        # confirm that the NFTokenOffer was actually created
        account_objects_response = await client.request(
            AccountObjects(
                account=nftoken_owner_wallet.address, type=AccountObjectType.NFT_OFFER
            )
        )
        self.assertTrue(len(account_objects_response.result["account_objects"]) > 0)
