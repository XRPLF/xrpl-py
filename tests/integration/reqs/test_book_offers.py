try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import ASYNC_JSON_RPC_CLIENT, JSON_RPC_CLIENT
from tests.integration.reusable_values import WALLET
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.requests import BookOffers


class TestBookOffers(IsolatedAsyncioTestCase):
    def test_basic_functionality_sync(self):
        response = JSON_RPC_CLIENT.request(
            BookOffers(
                taker=WALLET.classic_address,
                taker_gets=XRP(),
                taker_pays=IssuedCurrency(
                    currency="USD",
                    issuer="rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                ),
                ledger_index="validated",
            ),
        )
        self.assertTrue(response.is_successful())

    async def test_basic_functionality_async(self):
        response = await ASYNC_JSON_RPC_CLIENT.request(
            BookOffers(
                taker=WALLET.classic_address,
                taker_gets=XRP(),
                taker_pays=IssuedCurrency(
                    currency="USD",
                    issuer="rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                ),
                ledger_index="validated",
            ),
        )
        self.assertTrue(response.is_successful())
