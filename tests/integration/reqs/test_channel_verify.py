from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import ASYNC_JSON_RPC_CLIENT, JSON_RPC_CLIENT
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.models.requests import ChannelVerify


class TestChannelVerify(IsolatedAsyncioTestCase):
    def test_basic_functionality_sync(self):
        response = JSON_RPC_CLIENT.request(
            ChannelVerify(
                channel_id=PAYMENT_CHANNEL.result["hash"],
                amount="1",
                public_key=WALLET.public_key,
                signature="304402204EF0AFB78AC23ED1C472E74F4299C0C21",
            ),
        )
        self.assertTrue(response.is_successful())

    async def test_basic_functionality_async(self):
        response = await ASYNC_JSON_RPC_CLIENT.request(
            ChannelVerify(
                channel_id=PAYMENT_CHANNEL.result["hash"],
                amount="1",
                public_key=WALLET.public_key,
                signature="304402204EF0AFB78AC23ED1C472E74F4299C0C21",
            ),
        )
        self.assertTrue(response.is_successful())
