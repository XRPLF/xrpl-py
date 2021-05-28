from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from xrpl.models.requests import ServerInfo


class TestServerInfo(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(ServerInfo())
        self.assertTrue(response.is_successful())
