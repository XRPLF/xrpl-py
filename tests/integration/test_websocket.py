import asyncio
from unittest import TestCase

from tests.integration.it_utils import WEBSOCKET_CLIENT
from xrpl.ledger import get_fee


class TestWebsocket(TestCase):
    def test_get_fee(self):
        print(get_fee(WEBSOCKET_CLIENT))

    def test_connection(self):
        async def test():
            def handler(message: str) -> None:
                print(type(message))
                print(message)

            handler = asyncio.create_task(WEBSOCKET_CLIENT.handle_async(handler))
            send = asyncio.create_task(WEBSOCKET_CLIENT.send("message"))

            print("starting")
            await handler
            print("set up")
            await send
            print("sent?")
            WEBSOCKET_CLIENT.close()

        asyncio.get_event_loop().run_until_complete(test())
