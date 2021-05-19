import asyncio
from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import JSON_RPC_CLIENT, WEBSOCKET_CLIENT
from xrpl.asyncio.ledger import get_fee, get_latest_open_ledger_sequence
from xrpl.models.requests import StreamParameter, Subscribe


class TestWebsocket(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await WEBSOCKET_CLIENT.open()

    async def asyncTearDown(self):
        await WEBSOCKET_CLIENT.close()

    async def test_get_fee(self):
        a, b = await asyncio.gather(get_fee(WEBSOCKET_CLIENT), get_fee(JSON_RPC_CLIENT))
        self.assertEqual(a, b)

    async def test_get_latest_open_ledger_sequence(self):
        a, b = await asyncio.gather(
            get_latest_open_ledger_sequence(WEBSOCKET_CLIENT),
            get_latest_open_ledger_sequence(JSON_RPC_CLIENT),
        )
        self.assertEqual(a, b)

    async def test_connection(self):
        subscribe = Subscribe(streams=[StreamParameter.LEDGER])
        subscribe2 = Subscribe(accounts=["rJHjA2WqqYWSh4ttCPW1b9aSyFkisfz93j"])
        await asyncio.gather(
            WEBSOCKET_CLIENT.send(subscribe),
            WEBSOCKET_CLIENT.send(subscribe2),
        )
        async for message in WEBSOCKET_CLIENT:
            break
        self.assertEqual(True, True)
