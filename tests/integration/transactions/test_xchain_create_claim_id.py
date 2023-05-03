from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import BRIDGE
from xrpl.models import AccountObjects, AccountObjectType, XChainCreateClaimID
from xrpl.wallet import Wallet


class TestXChainCreateClaimID(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        account = Wallet.create()
        await fund_wallet_async(account)
        response = await sign_and_reliable_submission_async(
            XChainCreateClaimID(
                account=account.classic_address,
                xchain_bridge=BRIDGE.xchain_bridge,
                other_chain_source=Wallet.create().classic_address,
                signature_reward=BRIDGE.signature_reward,
            ),
            account,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_objects_response = await client.request(
            AccountObjects(
                account=account.classic_address,
                type=AccountObjectType.XCHAIN_OWNED_CLAIM_ID,
            )
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
