"""Performance testing of Websocket clients."""

from __future__ import annotations

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.requests import BookOffers
from xrpl.models.response import ResponseStatus


class TestWebsocketClient(IntegrationTestCase):
    """Memory usage of websocket client"""

    @test_async_and_sync(globals(), websockets_only=True)
    async def test_msg_queue_growth_websocket_client(self, client):
        """Test the rate of growth of the Message queue in websocket_client under
        persistent load. Admittedly, this is not a precise measure, rather its a proxy
        to measure the memory footprint of the client
        """

        for _ in range(5):
            response = await client.request(
                BookOffers(
                    ledger_index="current",
                    taker_gets=XRP(),
                    taker_pays=IssuedCurrency(
                        currency="USD", issuer="rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq"
                    ),
                    limit=500,
                )
            )

            self.assertEqual(response.status, ResponseStatus.SUCCESS)

            response = await client.request(
                BookOffers(
                    ledger_index="current",
                    taker_gets=IssuedCurrency(
                        currency="USD", issuer="rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq"
                    ),
                    taker_pays=XRP(),
                    limit=500,
                )
            )
            self.assertEqual(response.status, ResponseStatus.SUCCESS)

            self.assertEqual(client._messages.qsize(), 0)

        # the messages queue has not increased in proportion to the requests/responses
        # input load
        self.assertEqual(client._messages.qsize(), 0)
