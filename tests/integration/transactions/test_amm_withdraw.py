from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import (
    AMM_ASSET,
    AMM_ASSET2,
    AMM_ISSUER_WALLET,
    WALLET,
)
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.requests.amm_info import AMMInfo
from xrpl.models.transactions.amm_withdraw import AMMWithdraw, AMMWithdrawFlag

asset = AMM_ASSET
asset2 = AMM_ASSET2
issuer_wallet = AMM_ISSUER_WALLET


class TestAMMWithdraw(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_single_asset(self, client):
        pre_amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        response = await sign_and_reliable_submission_async(
            AMMWithdraw(
                account=WALLET.classic_address,
                asset=asset,
                asset2=asset2,
                amount="500",
                flags=AMMWithdrawFlag.TF_SINGLE_ASSET,
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

        self.assertLess(
            float(amm_info.result["amm"]["amount"]),
            float(pre_amm_info.result["amm"]["amount"]),
        )
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            pre_amm_info.result["amm"]["amount2"],
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )

    @test_async_and_sync(globals())
    async def test_two_assets(self, client):
        pre_amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        response = await sign_and_reliable_submission_async(
            AMMWithdraw(
                account=WALLET.classic_address,
                asset=asset,
                asset2=asset2,
                amount="50",
                amount2=IssuedCurrencyAmount(
                    currency=asset2.currency,
                    issuer=asset2.issuer,
                    value="50",
                ),
                flags=AMMWithdrawFlag.TF_TWO_ASSET,
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

        self.assertLess(
            float(amm_info.result["amm"]["amount"]),
            float(pre_amm_info.result["amm"]["amount"]),
        )
        self.assertLess(
            float(amm_info.result["amm"]["amount2"]["value"]),
            float(pre_amm_info.result["amm"]["amount2"]["value"]),
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )

    @test_async_and_sync(globals())
    async def test_one_asset_with_lptoken(self, client):
        pre_amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        lp_token = pre_amm_info.result["amm"]["lp_token"]

        response = await sign_and_reliable_submission_async(
            AMMWithdraw(
                account=WALLET.classic_address,
                asset=asset,
                asset2=asset2,
                amount="5",
                lp_token_in=IssuedCurrencyAmount(
                    currency=lp_token["currency"],
                    issuer=lp_token["issuer"],
                    value="5",
                ),
                flags=AMMWithdrawFlag.TF_ONE_ASSET_LP_TOKEN,
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

        self.assertLess(
            float(amm_info.result["amm"]["amount"]),
            float(pre_amm_info.result["amm"]["amount"]),
        )
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            pre_amm_info.result["amm"]["amount2"],
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )

    @test_async_and_sync(globals())
    async def test_lptoken(self, client):
        pre_amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        lp_token = pre_amm_info.result["amm"]["lp_token"]

        response = await sign_and_reliable_submission_async(
            AMMWithdraw(
                account=WALLET.classic_address,
                asset=asset,
                asset2=asset2,
                lp_token_in=IssuedCurrencyAmount(
                    currency=lp_token["currency"],
                    issuer=lp_token["issuer"],
                    value="5",
                ),
                flags=AMMWithdrawFlag.TF_LP_TOKEN,
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

        self.assertLess(
            float(amm_info.result["amm"]["amount"]),
            float(pre_amm_info.result["amm"]["amount"]),
        )
        self.assertLess(
            float(amm_info.result["amm"]["amount2"]["value"]),
            float(pre_amm_info.result["amm"]["amount2"]["value"]),
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )
