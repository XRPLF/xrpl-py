try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.models.requests import ChannelVerify


class TestChannelVerify(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
            ChannelVerify(
                channel_id=PAYMENT_CHANNEL.result["hash"],
                amount="1",
                public_key=WALLET.public_key,
                signature="304402204EF0AFB78AC23ED1C472E74F4299C0C21",
            ),
        )
        self.assertTrue(response.is_successful())
