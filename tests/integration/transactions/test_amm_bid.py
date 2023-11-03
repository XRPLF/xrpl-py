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
from xrpl.models.auth_account import AuthAccount
from xrpl.models.requests.amm_info import AMMInfo
from xrpl.models.transactions.amm_bid import AMMBid

asset = AMM_ASSET
asset2 = AMM_ASSET2
issuer_wallet = AMM_ISSUER_WALLET


class TestAMMBid(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
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

        before_price = float(
            pre_amm_info.result["amm"]["auction_slot"]["price"]["value"]
        )
        diff_price = -0.002891202555
        expected_price = before_price + diff_price

        before_lptoken = float(pre_amm_info.result["amm"]["lp_token"]["value"])
        diff_lptoken = -0.003099233161
        expected_lptoken = before_lptoken + diff_lptoken

        self.assertGreater(
            float(amm_info.result["amm"]["auction_slot"]["price"]["value"]),
            before_price,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["auction_slot"]["price"]["value"],
                expected_price,
                0.31212452270475843,
            )
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            before_lptoken,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["lp_token"]["value"],
                expected_lptoken,
                0.6109616023928766,
            )
        )

    @test_async_and_sync(globals())
    async def test_with_auth_account_bidmin_bidmax(self, client):
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

        before_price_value = float(
            pre_amm_info.result["amm"]["auction_slot"]["price"]["value"]
        )
        diff_price_value = 1.4462339482
        expected_price = before_price_value + diff_price_value

        before_lptoken_value = float(pre_amm_info.result["amm"]["lp_token"]["value"])
        diff_lptoken_value = -1.6435111096
        expected_lptoken_value = before_lptoken_value + diff_lptoken_value

        self.assertGreater(
            float(amm_info.result["amm"]["auction_slot"]["price"]["value"]),
            before_price_value,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["auction_slot"]["price"]["value"],
                expected_price,
                3.5493258038256785,
            )
        )
        self.assertLess(
            float(amm_info.result["amm"]["lp_token"]["value"]),
            before_lptoken_value,
        )
        self.assertTrue(
            compare_amm_values(
                amm_info.result["amm"]["lp_token"]["value"],
                expected_lptoken_value,
                3.352270654824224,
            )
        )
        self.assertEqual(
            amm_info.result["amm"]["auction_slot"]["auth_accounts"],
            [{"account": issuer_wallet.classic_address}],
        )
