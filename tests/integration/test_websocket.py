from asyncio import sleep
from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import JSON_RPC_CLIENT, WEBSOCKET_CLIENT
from xrpl.ledger import get_fee
from xrpl.models.requests import StreamParameter, Subscribe


class TestWebsocket(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await WEBSOCKET_CLIENT.open_async()

    async def asyncTearDown(self):
        await WEBSOCKET_CLIENT.close_async()

    def test_get_fee(self):
        self.assertEqual(get_fee(WEBSOCKET_CLIENT), get_fee(JSON_RPC_CLIENT))

    async def test_connection(self):
        id_val = "stream_test"
        subscribe = Subscribe(id=id_val, streams=[StreamParameter.LEDGER])
        await WEBSOCKET_CLIENT.send(subscribe)
        subscribe2 = Subscribe(
            id="test2", accounts=["rJHjA2WqqYWSh4ttCPW1b9aSyFkisfz93j"]
        )
        await WEBSOCKET_CLIENT.send(subscribe2)
        await sleep(4)
