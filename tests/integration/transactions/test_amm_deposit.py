from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import AMM, WALLET
from xrpl.models import AMMDeposit
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.requests.amm_info import AMMInfo
from xrpl.models.transactions.amm_deposit import AMMDepositFlag


class TestAMMCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_single_asset(self, client):
        asset = AMM["asset"]
        asset2 = AMM["asset2"]

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

        self.assertGreater(
            float(amm_info.result["amm"]["amount"]),
            float(pre_amm_info.result["amm"]["amount"]),
        )
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            pre_amm_info.result["amm"]["amount2"],
        )
        self.assertGreater(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )

    @test_async_and_sync(globals())
    async def test_two_assets(self, client):
        issuer_wallet = AMM["issuer_wallet"]
        asset = AMM["asset"]
        asset2 = AMM["asset2"]

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

        self.assertGreater(
            float(amm_info.result["amm"]["amount"]),
            float(pre_amm_info.result["amm"]["amount"]),
        )
        self.assertGreater(
            float(amm_info.result["amm"]["amount2"]["value"]),
            float(pre_amm_info.result["amm"]["amount2"]["value"]),
        )
        self.assertGreater(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )

    @test_async_and_sync(globals())
    async def test_one_asset_with_lptoken(self, client):
        issuer_wallet = AMM["issuer_wallet"]
        asset = AMM["asset"]
        asset2 = AMM["asset2"]

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

        self.assertGreater(
            float(amm_info.result["amm"]["amount"]),
            float(pre_amm_info.result["amm"]["amount"]),
        )
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            pre_amm_info.result["amm"]["amount2"],
        )
        self.assertGreater(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )

    @test_async_and_sync(globals())
    async def test_lptoken(self, client):
        issuer_wallet = AMM["issuer_wallet"]
        asset = AMM["asset"]
        asset2 = AMM["asset2"]

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

        self.assertGreater(
            float(amm_info.result["amm"]["amount"]),
            float(pre_amm_info.result["amm"]["amount"]),
        )
        self.assertGreater(
            float(amm_info.result["amm"]["amount2"]["value"]),
            float(pre_amm_info.result["amm"]["amount2"]["value"]),
        )
        self.assertGreater(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )
