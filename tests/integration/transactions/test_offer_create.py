try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import OfferCreate


class TestOfferCreate(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        offer = await submit_transaction_async(
            OfferCreate(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                taker_gets="13100000",
                taker_pays=IssuedCurrencyAmount(
                    currency="USD",
                    issuer=WALLET.classic_address,
                    value="10",
                ),
            ),
            WALLET,
        )
        self.assertTrue(offer.is_successful())
        WALLET.sequence += 1
