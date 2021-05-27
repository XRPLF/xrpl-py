try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import OFFER
from xrpl.models.requests import Tx


class TestTx(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
            Tx(
                transaction=OFFER.result["hash"],
            ),
        )
        self.assertTrue(response.is_successful())
