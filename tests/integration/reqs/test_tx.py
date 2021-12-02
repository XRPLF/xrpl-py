from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import OFFER
from xrpl.models.requests import Tx


class TestTx(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
            Tx(
                transaction=OFFER.result["tx_json"]["hash"],
            ),
        )
        self.assertTrue(response.is_successful())
