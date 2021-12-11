from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from xrpl.asyncio.ledger import get_fee
from xrpl.utils import drops_to_xrp


class TestLedger(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.ledger.get_fee"])
    async def test_get_fee_max(self, client):
        expected = "1"
        max_fee = drops_to_xrp(expected)
        result = await get_fee(client, max_fee=max_fee)
        self.assertEqual(result, expected)
