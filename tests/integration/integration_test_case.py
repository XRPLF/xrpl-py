try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import DEV_WEBSOCKET_CLIENT, WEBSOCKET_CLIENT


class IntegrationTestCase(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        WEBSOCKET_CLIENT.open()

    @classmethod
    def tearDownClass(cls):
        WEBSOCKET_CLIENT.close()


class DevIntegrationTestCase(IntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super(DevIntegrationTestCase, cls).setUpClass()
        DEV_WEBSOCKET_CLIENT.open()

    @classmethod
    def tearDownClass(cls):
        super(DevIntegrationTestCase, cls).tearDownClass()
        DEV_WEBSOCKET_CLIENT.close()
