try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase  # type: ignore

from tests.integration.it_utils import WEBSOCKET_CLIENT, WEBSOCKET_TESTNET_CLIENT


class IntegrationTestCase(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        WEBSOCKET_CLIENT.open()
        WEBSOCKET_TESTNET_CLIENT.open()

    @classmethod
    def tearDownClass(cls):
        WEBSOCKET_CLIENT.close()
        WEBSOCKET_TESTNET_CLIENT.close()
