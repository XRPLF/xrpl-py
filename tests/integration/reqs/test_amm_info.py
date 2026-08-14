from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_amm_pool_with_mpt_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import AMM_ASSET, AMM_ASSET2
from xrpl.models.requests.amm_info import AMMInfo

asset = AMM_ASSET
asset2 = AMM_ASSET2


class TestAMMInfo(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        self.assertEqual(float(amm_info.result["amm"]["amount"]), 1250)
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            {
                "currency": asset2.currency,
                "issuer": asset2.issuer,
                "value": "250",
            },
        )

    @test_async_and_sync(globals())
    async def test_amm_info_with_mpt_assets(self, client):
        amm_pool = await create_amm_pool_with_mpt_async(client)
        mpt_asset = amm_pool["asset"]
        mpt_asset2 = amm_pool["asset2"]

        amm_info = await client.request(
            AMMInfo(
                asset=mpt_asset,
                asset2=mpt_asset2,
            )
        )

        amm = amm_info.result["amm"]

        self.assertEqual(
            amm["amount"],
            {
                "mpt_issuance_id": mpt_asset.mpt_issuance_id,
                "value": "250",
            },
        )
        self.assertEqual(
            amm["amount2"],
            {
                "mpt_issuance_id": mpt_asset2.mpt_issuance_id,
                "value": "250",
            },
        )
        self.assertEqual(amm["trading_fee"], 12)
        self.assertIn("lp_token", amm)
