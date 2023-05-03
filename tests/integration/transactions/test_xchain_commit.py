from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import BRIDGE, WALLET
from xrpl.models import AccountInfo, XChainCommit


class TestXChainCommit(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        locking_chain_door = BRIDGE.xchain_bridge.locking_chain_door
        account_info1 = await client.request(AccountInfo(account=locking_chain_door))
        initial_balance = int(account_info1.result["account_data"]["Balance"])
        amount = 1000000

        response = await sign_and_reliable_submission_async(
            XChainCommit(
                account=WALLET.classic_address,
                xchain_bridge=BRIDGE.xchain_bridge,
                amount=str(amount),
                xchain_claim_id=1,
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_info2 = await client.request(AccountInfo(account=locking_chain_door))
        final_balance = int(account_info2.result["account_data"]["Balance"])
        self.assertEqual(final_balance, initial_balance + amount)
