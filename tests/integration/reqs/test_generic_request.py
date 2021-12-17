from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from xrpl.models.requests import GenericRequest


class TestGenericRequest(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_constructor(self, client):
        response = await client.request(
            GenericRequest(
                method="tx_history",
                start=0,
            )
        )
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_json_formatting(self, client):
        response = await client.request(
            GenericRequest.from_dict(
                {
                    "method": "tx_history",
                    "params": {
                        "start": 0,
                    },
                }
            )
        )
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_websocket_formatting(self, client):
        response = await client.request(
            GenericRequest.from_dict(
                {
                    "command": "tx_history",
                    "start": 0,
                }
            )
        )
        self.assertTrue(response.is_successful())
