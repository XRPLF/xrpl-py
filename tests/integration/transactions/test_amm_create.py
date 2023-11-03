from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import create_amm_pool_async, test_async_and_sync
from xrpl.models.requests.amm_info import AMMInfo


class TestAMMCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        amm_pool = await create_amm_pool_async(client)
        asset = amm_pool["asset"]
        asset2 = amm_pool["asset2"]

        amm_info = await client.request(
            AMMInfo(
                asset=asset,
                asset2=asset2,
            )
        )

        self.assertEqual(float(amm_info.result["amm"]["amount"]), 250)
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            {
                "currency": asset2.currency,
                "issuer": asset2.issuer,
                "value": "250",
            },
        )
