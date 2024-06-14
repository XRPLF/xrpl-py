"""Memory usage of Websocket clients."""

from __future__ import annotations

import asyncio
from unittest import TestCase

from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.clients.websocket_client import WebsocketClient
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.requests import BookOffers

try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase  # type: ignore


class TestAsyncWebsocketClient(IsolatedAsyncioTestCase):
    """Memory usage of async-websocket client"""

    async def test_msg_queue_async_websocket_client(
        self: TestAsyncWebsocketClient,
    ) -> None:
        """Test the rate of growth of the Message queue in async_websocket_client under
        persistent load. Admittedly, this is not a precise measure, rather its a proxy
        to measure the memory footprint of the client
        """
        async with AsyncWebsocketClient("wss://s1.ripple.com") as client:
            for _ in range(5):
                await client.request(
                    BookOffers(
                        ledger_index="current",
                        taker_gets=XRP(),
                        taker_pays=IssuedCurrency(
                            currency="USD", issuer="rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq"
                        ),
                        limit=500,
                    )
                )

                await client.request(
                    BookOffers(
                        ledger_index="current",
                        taker_gets=IssuedCurrency(
                            currency="USD", issuer="rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq"
                        ),
                        taker_pays=XRP(),
                        limit=500,
                    )
                )

                self.assertEqual(client._messages.qsize(), 0)
                await asyncio.sleep(2)


class TestSyncWebsocketClient(TestCase):
    """Memory usage of sync-websocket client"""

    def test_msg_queue_sync_websocket_client(
        self: TestSyncWebsocketClient,
    ) -> None:
        """Test the rate of growth of the Message queue in sync_websocket_client under
        persistent load. Admittedly, this is not a precise measure, rather its a proxy
        to measure the memory footprint of the client
        """
        with WebsocketClient("wss://s1.ripple.com") as client:
            for _ in range(5):
                client.request(
                    BookOffers(
                        ledger_index="current",
                        taker_gets=XRP(),
                        taker_pays=IssuedCurrency(
                            currency="USD", issuer="rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq"
                        ),
                        limit=500,
                    )
                )

                client.request(
                    BookOffers(
                        ledger_index="current",
                        taker_gets=IssuedCurrency(
                            currency="USD", issuer="rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq"
                        ),
                        taker_pays=XRP(),
                        limit=500,
                    )
                )

                self.assertEqual(client._messages.qsize(), 0)
