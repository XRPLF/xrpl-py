from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import VaultCreate
from xrpl.models.response import ResponseStatus


class TestSingleAssetVault(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_sav_lifecycle(self, client):

        # Create a vault
        tx = VaultCreate(
            account=WALLET.address,
            asset="100",
            asset_maximum="1000",
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Verify the existence of the vault with account_objects RPC call

        # Update the characteristics of the vault with VaultSet transaction

        # Execute a VaultDeposit transaction

        # Execute a VaultWithdraw transaction

        # Execute a VaultClawback transaction

        # Delete the Vault with VaultDelete transaction

        # # confirm that the DID was actually created
        # account_objects_response = await client.request(
        #     AccountObjects(account=WALLET.address, type=AccountObjectType.DID)
        # )
        # self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
