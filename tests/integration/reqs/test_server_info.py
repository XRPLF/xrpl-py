try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import test_async_and_sync
from xrpl.models.requests import ServerInfo


class TestServerInfo(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(ServerInfo())
        self.assertTrue(response.is_successful())
