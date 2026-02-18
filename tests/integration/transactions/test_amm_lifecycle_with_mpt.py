from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_amm_pool_with_mpt_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.amounts import MPTAmount
from xrpl.models.requests.amm_info import AMMInfo
from xrpl.models.transactions.amm_clawback import AMMClawback
from xrpl.models.transactions.amm_deposit import AMMDeposit, AMMDepositFlag
from xrpl.models.transactions.amm_withdraw import AMMWithdraw, AMMWithdrawFlag


class TestAMMLifecycleWithMPT(IntegrationTestCase):
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

    @test_async_and_sync(globals())
    async def test_mpt_amm_withdraw_single_asset(self, client):
        amm_pool = await create_amm_pool_with_mpt_async(client)
        asset = amm_pool["asset"]
        asset2 = amm_pool["asset2"]
        lp_wallet = amm_pool["lp_wallet"]

        pre_amm_info = await client.request(AMMInfo(asset=asset, asset2=asset2))
        pre_amm = pre_amm_info.result["amm"]
        before_amount = int(pre_amm["amount"]["value"])
        before_amount2 = int(pre_amm["amount2"]["value"])
        before_lp_token_value = float(pre_amm["lp_token"]["value"])

        withdraw_value = "50"
        response = await sign_and_reliable_submission_async(
            AMMWithdraw(
                account=lp_wallet.classic_address,
                asset=asset,
                asset2=asset2,
                amount=MPTAmount(
                    mpt_issuance_id=asset.mpt_issuance_id,
                    value=withdraw_value,
                ),
                flags=AMMWithdrawFlag.TF_SINGLE_ASSET,
            ),
            lp_wallet,
            client,
        )

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        post_amm_info = await client.request(AMMInfo(asset=asset, asset2=asset2))
        post_amm = post_amm_info.result["amm"]

        # The withdrawn asset's pool balance should decrease by the withdraw amount
        self.assertEqual(
            int(post_amm["amount"]["value"]),
            before_amount - int(withdraw_value),
        )
        # The other asset's pool balance should remain unchanged
        self.assertEqual(int(post_amm["amount2"]["value"]), before_amount2)
        # LP token supply should decrease after the withdrawal
        self.assertLess(
            float(post_amm["lp_token"]["value"]),
            before_lp_token_value,
        )

    @test_async_and_sync(globals())
    async def test_mpt_amm_delete(self, client):
        amm_pool = await create_amm_pool_with_mpt_async(client)
        asset = amm_pool["asset"]
        asset2 = amm_pool["asset2"]
        lp_wallet = amm_pool["lp_wallet"]

        # Withdraw all assets to empty the pool
        # Note: Withdrawal of all the assets (i.e outstanding LPTokens = 0) in the AMM
        # pool will delete the AMM.
        response = await sign_and_reliable_submission_async(
            AMMWithdraw(
                account=lp_wallet.classic_address,
                asset=asset,
                asset2=asset2,
                flags=AMMWithdrawFlag.TF_WITHDRAW_ALL,
            ),
            lp_wallet,
            client,
        )

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Verify the AMM no longer exists
        amm_info = await client.request(AMMInfo(asset=asset, asset2=asset2))
        self.assertEqual(amm_info.result["error"], "actNotFound")

    @test_async_and_sync(globals())
    async def test_mpt_amm_clawback(self, client):
        amm_pool = await create_amm_pool_with_mpt_async(
            client,
        )
        asset = amm_pool["asset"]
        asset2 = amm_pool["asset2"]
        issuer_wallet = amm_pool["issuer_wallet_1"]
        holder_wallet = amm_pool["lp_wallet"]

        # Holder deposits more of asset into the AMM
        await sign_and_reliable_submission_async(
            AMMDeposit(
                account=holder_wallet.classic_address,
                asset=asset,
                asset2=asset2,
                amount=MPTAmount(
                    mpt_issuance_id=asset.mpt_issuance_id,
                    value="10",
                ),
                flags=AMMDepositFlag.TF_SINGLE_ASSET,
            ),
            holder_wallet,
            client,
        )

        pre_amm_info = await client.request(AMMInfo(asset=asset, asset2=asset2))
        pre_amm = pre_amm_info.result["amm"]
        before_amount = int(pre_amm["amount"]["value"])

        # Issuer claws back holder's share of asset from the AMM
        response = await sign_and_reliable_submission_async(
            AMMClawback(
                account=issuer_wallet.classic_address,
                holder=holder_wallet.classic_address,
                asset=asset,
                asset2=asset2,
                amount=MPTAmount(
                    mpt_issuance_id=asset.mpt_issuance_id,
                    value="10",
                ),
            ),
            issuer_wallet,
            client,
        )

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Pool's balance of the clawed-back asset should decrease
        post_amm_info = await client.request(AMMInfo(asset=asset, asset2=asset2))
        post_amm = post_amm_info.result["amm"]
        self.assertLess(int(post_amm["amount"]["value"]), before_amount)
