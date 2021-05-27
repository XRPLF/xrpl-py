try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import ASYNC_JSON_RPC_CLIENT, JSON_RPC_CLIENT
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.requests import RipplePathFind


class TestRipplePathFind(IsolatedAsyncioTestCase):
    def test_basic_functionality_sync(self):
        response = JSON_RPC_CLIENT.request(
            RipplePathFind(
                source_account=WALLET.classic_address,
                destination_account=DESTINATION.classic_address,
                destination_amount="100",
            ),
        )
        self.assertTrue(response.is_successful())

    async def test_basic_functionality_async(self):
        response = await ASYNC_JSON_RPC_CLIENT.request(
            RipplePathFind(
                source_account=WALLET.classic_address,
                destination_account=DESTINATION.classic_address,
                destination_amount="100",
            ),
        )
        self.assertTrue(response.is_successful())
