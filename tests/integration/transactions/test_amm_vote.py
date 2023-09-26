from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import AMM, WALLET
from xrpl.models.requests.amm_info import AMMInfo
from xrpl.models.transactions.amm_deposit import AMMDeposit, AMMDepositFlag
from xrpl.models.transactions.amm_vote import AMMVote


class TestAMMVote(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        asset = AMM["asset"]
        asset2 = AMM["asset2"]

        # Need to deposit (be an LP) before voting is eligible
        response = await sign_and_reliable_submission_async(
            AMMDeposit(
                account=WALLET.classic_address,
                asset=asset,
                asset2=asset2,
                amount="1000",
                flags=AMMDepositFlag.TF_SINGLE_ASSET,
            ),
            WALLET,
            client,
        )

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        pre_amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        response = await sign_and_reliable_submission_async(
            AMMVote(
                account=WALLET.classic_address,
                asset=asset,
                asset2=asset2,
                trading_fee=pre_amm_info.result["amm"]["trading_fee"] + 10,
            ),
            WALLET,
            client,
        )

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        self.assertGreater(
            amm_info.result["amm"]["trading_fee"],
            pre_amm_info.result["amm"]["trading_fee"],
        )
        self.assertEqual(len(amm_info.result["amm"]["vote_slots"]), 2)
