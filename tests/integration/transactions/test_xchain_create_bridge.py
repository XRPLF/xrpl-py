from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    MASTER_ACCOUNT,
    fund_wallet_async,
    submit_transaction_async,
    test_async_and_sync,
)
from xrpl.models import (
    XRP,
    AccountObjects,
    AccountObjectType,
    XChainBridge,
    XChainCreateBridge,
)
from xrpl.wallet import Wallet


class TestXChainCreateBridge(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        door_wallet = Wallet.create()
        await fund_wallet_async(door_wallet)
        response = await submit_transaction_async(
            XChainCreateBridge(
                account=door_wallet.classic_address,
                xchain_bridge=XChainBridge(
                    locking_chain_door=door_wallet.classic_address,
                    locking_chain_issue=XRP(),
                    issuing_chain_door=MASTER_ACCOUNT,
                    issuing_chain_issue=XRP(),
                ),
                signature_reward="200",
                min_account_create_amount="10000000",
            ),
            door_wallet,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_objects_response = await client.request(
            AccountObjects(
                account=door_wallet.classic_address, type=AccountObjectType.BRIDGE
            )
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
