from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async
from tests.integration.reusable_values import OFFER, WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import OfferCreate


class TestOfferCreate(IsolatedAsyncioTestCase):
    def test_basic_functionality(self):
        # we already create this elsewhere
        self.assertTrue(OFFER.is_successful())

    async def test_basic_functionality_async(self):
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
