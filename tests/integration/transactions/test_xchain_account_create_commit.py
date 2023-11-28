from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import BRIDGE, WALLET
from xrpl.models import AccountInfo, XChainAccountCreateCommit
from xrpl.wallet import Wallet


class TestXChainAccountCreateCommit(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        locking_chain_door = BRIDGE.xchain_bridge.locking_chain_door
        account_info1 = await client.request(AccountInfo(account=locking_chain_door))
        initial_balance = int(account_info1.result["account_data"]["Balance"])
        amount = int(BRIDGE.min_account_create_amount)

        response = await sign_and_reliable_submission_async(
            XChainAccountCreateCommit(
                account=WALLET.classic_address,
                xchain_bridge=BRIDGE.xchain_bridge,
                amount=str(amount),
                signature_reward=BRIDGE.signature_reward,
                destination=Wallet.create().classic_address,
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_info2 = await client.request(AccountInfo(account=locking_chain_door))
        final_balance = int(account_info2.result["account_data"]["Balance"])
        self.assertEqual(
            final_balance, initial_balance + amount + int(BRIDGE.signature_reward)
        )
