from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import AMM_ASSET, AMM_ASSET2
from xrpl.models.requests.amm_info import AMMInfo

asset = AMM_ASSET
asset2 = AMM_ASSET2


class TestAMMCreate(IntegrationTestCase):
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
