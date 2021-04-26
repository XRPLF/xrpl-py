from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT, WEBSOCKET_CLIENT, WEBSOCKET_URL
from xrpl.clients import WebsocketClient
from xrpl.ledger import get_fee
from xrpl.models.requests import StreamParameter, Subscribe


class TestWebsocket(TestCase):
    def test_get_fee(self):
        self.assertEqual(get_fee(WEBSOCKET_CLIENT), get_fee(JSON_RPC_CLIENT))

    def test_connection(self):
        websocket = WebsocketClient(WEBSOCKET_URL)
        id_val = "stream_test"

        def handler(response):
            self.assertEqual(response.status, "success")
            self.assertEqual(response.id, id_val)
            websocket.close()

        subscribe = Subscribe(id=id_val, streams=[StreamParameter.LEDGER])
        websocket.listen(subscribe, handler)
