from unittest import TestCase

from tests.integrations.it_utils import WEBSOCKET_CLIENT
from xrpl.ledger import get_fee


class TestWebsocket(TestCase):
    def test_get_fee(self):
        print(get_fee(WEBSOCKET_CLIENT))
