try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.requests import BookOffers


class TestBookOffers(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
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
