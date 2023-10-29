from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    compare_amm_values,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import (
    AMM_ASSET,
    AMM_ASSET2,
    AMM_ISSUER_WALLET,
    WALLET,
)
from xrpl.models.requests.amm_info import AMMInfo
from xrpl.models.transactions.amm_vote import AMMVote

asset = AMM_ASSET
asset2 = AMM_ASSET2
issuer_wallet = AMM_ISSUER_WALLET


class TestAMMVote(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
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

        before_trading_fee = pre_amm_info.result["amm"]["trading_fee"]
        diff_trading_fee = 5.75
        expected_trading_fee = before_trading_fee + diff_trading_fee

        self.assertGreater(
            amm_info.result["amm"]["trading_fee"],
            before_trading_fee,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["trading_fee"],
                expected_trading_fee,
                3.75,
            )
        )
        self.assertEqual(len(amm_info.result["amm"]["vote_slots"]), 2)
