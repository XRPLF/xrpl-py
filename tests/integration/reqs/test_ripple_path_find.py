try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.requests import RipplePathFind


class TestRipplePathFind(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
            RipplePathFind(
                source_account=WALLET.classic_address,
                destination_account=DESTINATION.classic_address,
                destination_amount="100",
            ),
        )
        self.assertTrue(response.is_successful())
