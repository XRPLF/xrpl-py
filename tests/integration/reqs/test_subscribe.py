from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from xrpl.models.requests import StreamParameter, Subscribe

MESSAGE_LIMIT = 3


class TestSubscribe(IntegrationTestCase):
    @test_async_and_sync(globals(), websockets_only=True)
    async def test_basic_functionality(self, client):
        req = Subscribe(streams=[StreamParameter.LEDGER])
        await client.send(req)
        count = 0
        async for message in client:
            if count > MESSAGE_LIMIT:
                break
            if count == 0:
                with self.subTest():
                    self.assertIsInstance(message["result"]["ledger_index"], int)
            else:
                with self.subTest():
                    self.assertIsInstance(message["ledger_index"], int)
            count = count + 1
