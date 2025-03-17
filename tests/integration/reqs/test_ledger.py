from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from xrpl.asyncio.ledger import get_latest_open_ledger_sequence
from xrpl.models.requests import Ledger


class TestLedger(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(Ledger())
        self.assertTrue(response.is_successful())

    @test_async_and_sync(
        globals(),
        ["xrpl.ledger.get_latest_open_ledger_sequence"],
        use_testnet=True,
    )
    async def test_fetch_current_ledger(self, client):
        response = await get_latest_open_ledger_sequence(client)
        self.assertTrue(isinstance(response, int))
