from asyncio import sleep
from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import JSON_RPC_CLIENT, WEBSOCKET_URL
from xrpl.clients import WebsocketClient
from xrpl.ledger import get_fee
from xrpl.models.requests import StreamParameter, Subscribe

websocket = WebsocketClient(WEBSOCKET_URL)


class TestWebsocket(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await websocket.open_async()

    async def asyncTearDown(self):
        await websocket.close_async()

    def test_get_fee(self):
        self.assertEqual(get_fee(websocket), get_fee(JSON_RPC_CLIENT))

    async def test_connection(self):
        print("running")
        id_val = "stream_test"
        subscribe = Subscribe(id=id_val, streams=[StreamParameter.LEDGER])
        await websocket.send(subscribe)
        subscribe2 = Subscribe(
            id="test2", accounts=["rJHjA2WqqYWSh4ttCPW1b9aSyFkisfz93j"]
        )
        await websocket.send(subscribe2)
        await sleep(4)
