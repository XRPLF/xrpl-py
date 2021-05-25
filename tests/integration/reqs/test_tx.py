from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import ASYNC_JSON_RPC_CLIENT, JSON_RPC_CLIENT
from tests.integration.reusable_values import OFFER
from xrpl.models.requests import Tx


class TestTx(IsolatedAsyncioTestCase):
    def test_basic_functionality_sync(self):
        response = JSON_RPC_CLIENT.request(
            Tx(
                transaction=OFFER.result["hash"],
            ),
        )
        self.assertTrue(response.is_successful())

    async def test_basic_functionality_async(self):
        response = await ASYNC_JSON_RPC_CLIENT.request(
            Tx(
                transaction=OFFER.result["hash"],
            ),
        )
        self.assertTrue(response.is_successful())
