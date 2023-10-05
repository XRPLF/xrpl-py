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
from xrpl.models import AMMDeposit
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.requests.amm_info import AMMInfo
from xrpl.models.transactions.amm_deposit import AMMDepositFlag

asset = AMM_ASSET
asset2 = AMM_ASSET2
issuer_wallet = AMM_ISSUER_WALLET


class TestAMMDeposit(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_single_asset(self, client):
        pre_amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

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

        amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        before_amount = float(pre_amm_info.result["amm"]["amount"])
        diff_amount = 1000
        expected_amount = before_amount + diff_amount

        before_lptoken_value = float(pre_amm_info.result["amm"]["lp_token"]["value"])
        diff_lptoken_value = 143.850763914
        expected_lptoken_value = before_lptoken_value + diff_lptoken_value

        self.assertEqual(float(amm_info.result["amm"]["amount"]), expected_amount)
        self.assertEqual(
            float(amm_info.result["amm"]["amount2"]["value"]),
            float(pre_amm_info.result["amm"]["amount2"]["value"]),
        )
        self.assertGreater(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            before_lptoken_value,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["lp_token"]["value"],
                expected_lptoken_value,
                41.016240932237565,
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
            AMMDeposit(
                account=issuer_wallet.classic_address,
                asset=asset,
                asset2=asset2,
                amount="100",
                amount2=IssuedCurrencyAmount(
                    currency=asset2.currency,
                    issuer=asset2.issuer,
                    value="100",
                ),
                flags=AMMDepositFlag.TF_TWO_ASSET,
            ),
            issuer_wallet,
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
        diff_amount = 100
        expected_amount = before_amount + diff_amount

        before_amount2_value = float(pre_amm_info.result["amm"]["amount2"]["value"])
        diff_amount2 = 5
        expected_amount2_value = before_amount2_value + diff_amount2

        before_lptoken_value = float(pre_amm_info.result["amm"]["lp_token"]["value"])
        diff_lptoken = 21.6824186193
        expected_lptoken_value = before_lptoken_value + diff_lptoken

        self.assertEqual(
            float(amm_info.result["amm"]["amount"]),
            expected_amount,
        )
        self.assertGreater(
            float(amm_info.result["amm"]["amount2"]["value"]),
            float(pre_amm_info.result["amm"]["amount2"]["value"]),
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["amount2"]["value"],
                expected_amount2_value,
                0.1902856440025289,
            )
        )
        self.assertGreater(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            before_lptoken_value,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["lp_token"]["value"],
                expected_lptoken_value,
                8.185452315956354e-12,
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
            AMMDeposit(
                account=issuer_wallet.classic_address,
                asset=asset,
                asset2=asset2,
                amount="100",
                lp_token_out=IssuedCurrencyAmount(
                    currency=lp_token["currency"],
                    issuer=lp_token["issuer"],
                    value="5",
                ),
                flags=AMMDepositFlag.TF_ONE_ASSET_LP_TOKEN,
            ),
            issuer_wallet,
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
        diff_amount = 23
        expected_amount = before_amount + diff_amount

        before_lptoken_value = float(pre_amm_info.result["amm"]["lp_token"]["value"])
        diff_lptoken = 5
        expected_lptoken_value = before_lptoken_value + diff_lptoken

        self.assertEqual(
            float(amm_info.result["amm"]["amount"]),
            expected_amount,
        )
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            pre_amm_info.result["amm"]["amount2"],
        )
        self.assertEqual(
            float(amm_info.result["amm"]["lp_token"]["value"]), expected_lptoken_value
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
            AMMDeposit(
                account=issuer_wallet.classic_address,
                asset=asset,
                asset2=asset2,
                lp_token_out=IssuedCurrencyAmount(
                    currency=lp_token["currency"],
                    issuer=lp_token["issuer"],
                    value="5",
                ),
                flags=AMMDepositFlag.TF_LP_TOKEN,
            ),
            issuer_wallet,
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
        diff_amount = 11
        expected_amount = before_amount + diff_amount

        before_amount2_value = float(pre_amm_info.result["amm"]["amount2"]["value"])
        diff_amount2_value = 2.2628038035
        expected_amount2_value = before_amount2_value + diff_amount2_value

        before_lptoken_value = float(pre_amm_info.result["amm"]["lp_token"]["value"])
        diff_lptoken_value = 5
        expected_lptoken_value = before_lptoken_value + diff_lptoken_value

        self.assertEqual(
            float(amm_info.result["amm"]["amount"]),
            expected_amount,
        )
        self.assertGreater(
            float(amm_info.result["amm"]["amount2"]["value"]),
            diff_amount2_value,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["amount2"]["value"],
                expected_amount2_value,
                8.924416761146858e-12,
            )
        )
        self.assertEqual(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            expected_lptoken_value,
        )
