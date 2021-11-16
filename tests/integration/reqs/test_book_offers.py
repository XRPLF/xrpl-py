from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.clients.utils import (
    json_to_response,
    request_to_json_rpc,
    request_to_websocket,
    websocket_to_response,
)
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.requests import BookOffers

_REQUEST = BookOffers(
    taker=WALLET.classic_address,
    taker_gets=XRP(),
    taker_pays=IssuedCurrency(
        currency="USD",
        issuer="rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
    ),
    ledger_index="validated",
)


class TestBookOffers(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(_REQUEST)
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_request_json(self, client):
        # TODO: run request_json tests via metaprogramming, instead of copy-paste
        is_websocket = "ws" in client.url
        if is_websocket:
            request = request_to_websocket(_REQUEST)
        else:
            request = request_to_json_rpc(_REQUEST)
        response = await client.request_json(request)
        if is_websocket:
            resp = websocket_to_response(response)
        else:
            resp = json_to_response(response)
        self.assertTrue(resp.is_successful())
