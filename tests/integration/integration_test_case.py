try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    print(globals())
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import WEBSOCKET_CLIENT


class IntegrationTestCase(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        WEBSOCKET_CLIENT.open()

    @classmethod
    def tearDownClass(cls):
        WEBSOCKET_CLIENT.close()
