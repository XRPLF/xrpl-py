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

        before_amount = float(pre_amm_info.result["amm"]["amount"])
        diff_amount = -500
        expected_amount = before_amount + diff_amount

        before_lptoken_value = float(pre_amm_info.result["amm"]["lp_token"]["value"])
        diff_lptoken_value = -61.2810042329
        expected_lptoken_value = before_lptoken_value + diff_lptoken_value

        self.assertEqual(
            float(amm_info.result["amm"]["amount"]),
            expected_amount,
        )
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            pre_amm_info.result["amm"]["amount2"],
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            before_lptoken_value,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["lp_token"]["value"],
                expected_lptoken_value,
                6.206379545573327,
            )
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

        before_amount = float(pre_amm_info.result["amm"]["amount"])
        diff_amount = -50
        expected_amount = before_amount + diff_amount

        before_amount2_value = float(pre_amm_info.result["amm"]["amount2"]["value"])
        diff_amount2_value = 3.8999367945
        expected_amount2_value = before_amount2_value + diff_amount2_value

        before_lptoken_value = float(pre_amm_info.result["amm"]["lp_token"]["value"])
        diff_lptoken_value = -13.805478843361811
        expected_lptoken_value = before_lptoken_value + diff_lptoken_value

        self.assertEqual(
            float(amm_info.result["amm"]["amount"]),
            expected_amount,
        )
        self.assertLess(
            float(amm_info.result["amm"]["amount2"]["value"]),
            before_amount2_value,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["amount2"]["value"],
                expected_amount2_value,
                7.799873589023093,
            )
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            before_lptoken_value,
        )
        self.assertTrue(
            compare_amm_values(
                float(amm_info.result["amm"]["lp_token"]["value"]),
                expected_lptoken_value,
                0.24811570097392632,
            )
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

        diff_amount = -45
        expected_amount = float(pre_amm_info.result["amm"]["amount"]) + diff_amount
        diff_lptoken = -5
        expected_lptoken = (
            float(pre_amm_info.result["amm"]["lp_token"]["value"]) + diff_lptoken
        )

        self.assertLess(
            float(amm_info.result["amm"]["amount"]),
            float(pre_amm_info.result["amm"]["amount"]),
        )
        self.assertTrue(
            compare_amm_values(
                float(amm_info.result["amm"]["amount"]),
                expected_amount,
                1,
            )
        )
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            pre_amm_info.result["amm"]["amount2"],
        )
        self.assertEqual(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            expected_lptoken,
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

        before_amount = float(pre_amm_info.result["amm"]["amount"])
        diff_amount = -23
        expected_amount = before_amount + diff_amount

        before_amount2_value = float(pre_amm_info.result["amm"]["amount2"]["value"])
        diff_amount2_value = -1.1091277317
        expected_amount2_value = before_amount2_value + diff_amount2_value

        before_lptoken_value = float(pre_amm_info.result["amm"]["lp_token"]["value"])
        diff_lptoken_value = -5
        expected_lptoken_value = before_lptoken_value + diff_lptoken_value

        self.assertEqual(
            float(amm_info.result["amm"]["amount"]),
            expected_amount,
        )
        self.assertLess(
            float(amm_info.result["amm"]["amount2"]["value"]),
            float(pre_amm_info.result["amm"]["amount2"]["value"]),
        )
        self.assertTrue(
            compare_amm_values(
                float(amm_info.result["amm"]["amount2"]["value"]),
                expected_amount2_value,
                0.012903907753866406,
            )
        )
        self.assertEqual(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            expected_lptoken_value,
        )
