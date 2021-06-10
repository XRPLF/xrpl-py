from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from xrpl.models.requests import StreamParameter, Subscribe
from xrpl.models.requests.unsubscribe import Unsubscribe

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
                self.assertIsInstance(message["result"]["ledger_index"], int)
            else:
                self.assertIsInstance(message["ledger_index"], int)
            count = count + 1
        req = Unsubscribe()
        await client.send(req)
