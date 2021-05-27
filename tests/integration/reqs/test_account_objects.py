try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import ASYNC_JSON_RPC_CLIENT, JSON_RPC_CLIENT
from tests.integration.reusable_values import WALLET
from xrpl.models.requests import AccountObjects


class TestAccountObjects(IsolatedAsyncioTestCase):
    def test_basic_functionality_sync(self):
        response = JSON_RPC_CLIENT.request(
            AccountObjects(
                account=WALLET.classic_address,
            )
        )
        self.assertTrue(response.is_successful())

    async def test_basic_functionality_async(self):
        response = await ASYNC_JSON_RPC_CLIENT.request(
            AccountObjects(
                account=WALLET.classic_address,
            )
        )
        self.assertTrue(response.is_successful())
