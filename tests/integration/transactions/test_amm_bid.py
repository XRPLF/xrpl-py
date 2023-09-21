from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import AMM, WALLET
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.auth_account import AuthAccount
from xrpl.models.requests.amm_info import AMMInfo
from xrpl.models.transactions.amm_bid import AMMBid
from xrpl.models.transactions.amm_deposit import AMMDeposit, AMMDepositFlag


class TestAMMBid(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        asset = AMM["asset"]
        asset2 = AMM["asset2"]

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
            AMMBid(
                account=WALLET.classic_address,
                asset=asset,
                asset2=asset2,
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
            float(amm_info.result["amm"]["auction_slot"]["price"]["value"]),
            float(pre_amm_info.result["amm"]["auction_slot"]["price"]["value"]),
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )

    @test_async_and_sync(globals())
    async def test_with_auth_account_bidmin_bidmax(self, client):
        issuer_wallet = AMM["issuer_wallet"]
        asset = AMM["asset"]
        asset2 = AMM["asset2"]

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
        lp_token = pre_amm_info.result["amm"]["lp_token"]

        response = await sign_and_reliable_submission_async(
            AMMBid(
                account=WALLET.classic_address,
                asset=asset,
                asset2=asset2,
                auth_accounts=[AuthAccount(account=issuer_wallet.classic_address)],
                bid_min=IssuedCurrencyAmount(
                    currency=lp_token["currency"],
                    issuer=lp_token["issuer"],
                    value="5",
                ),
                bid_max=IssuedCurrencyAmount(
                    currency=lp_token["currency"],
                    issuer=lp_token["issuer"],
                    value="10",
                ),
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
            float(amm_info.result["amm"]["auction_slot"]["price"]["value"]),
            float(pre_amm_info.result["amm"]["auction_slot"]["price"]["value"]),
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            float(pre_amm_info.result["amm"]["lp_token"]["value"]),
        )
        self.assertEqual(
            amm_info.result["amm"]["auction_slot"]["auth_accounts"],
            [{"account": issuer_wallet.classic_address}],
        )
