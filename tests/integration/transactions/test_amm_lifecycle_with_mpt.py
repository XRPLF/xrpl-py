from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_amm_pool_with_mpt,
    create_amm_pool_with_mpt_async,
    sign_and_reliable_submission,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.amounts import MPTAmount
from xrpl.models.requests.amm_info import AMMInfo
from xrpl.models.transactions.amm_deposit import AMMDeposit, AMMDepositFlag


class TestAMMCreateWithMPT(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_mpt_amm_pool(self, client):
        amm_pool = await create_amm_pool_with_mpt_async(client)
        asset = amm_pool["asset"]
        asset2 = amm_pool["asset2"]

        amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        print(amm_info)

        amm = amm_info.result["amm"]

        self.assertEqual(
            amm["amount"],
            {
                "mpt_issuance_id": asset.mpt_issuance_id,
                "value": "250",
            },
        )
        self.assertEqual(
            amm["amount2"],
            {
                "mpt_issuance_id": asset2.mpt_issuance_id,
                "value": "250",
            },
        )
        self.assertEqual(amm["trading_fee"], 12)

    @test_async_and_sync(globals())
    async def test_mpt_amm_deposit_single_asset(self, client):
        amm_pool = await create_amm_pool_with_mpt_async(client)
        asset = amm_pool["asset"]
        asset2 = amm_pool["asset2"]
        lp_wallet = amm_pool["lp_wallet"]

        pre_amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )
        pre_amm = pre_amm_info.result["amm"]
        before_amount = int(pre_amm["amount"]["value"])
        before_amount2 = int(pre_amm["amount2"]["value"])
        before_lp_token_value = float(pre_amm["lp_token"]["value"])

        deposit_value = "100"
        response = await sign_and_reliable_submission_async(
            AMMDeposit(
                account=lp_wallet.classic_address,
                asset=asset,
                asset2=asset2,
                amount=MPTAmount(
                    mpt_issuance_id=asset.mpt_issuance_id,
                    value=deposit_value,
                ),
                flags=AMMDepositFlag.TF_SINGLE_ASSET,
            ),
            lp_wallet,
            client,
        )

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        post_amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )
        post_amm = post_amm_info.result["amm"]

        # The deposited asset's pool balance should increase by the deposit amount
        self.assertEqual(
            int(post_amm["amount"]["value"]),
            before_amount + int(deposit_value),
        )
        # The other asset's pool balance should remain unchanged
        self.assertEqual(int(post_amm["amount2"]["value"]), before_amount2)
        # LP token supply should increase after the deposit
        self.assertGreater(
            float(post_amm["lp_token"]["value"]),
            before_lp_token_value,
        )
