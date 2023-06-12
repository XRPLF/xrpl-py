from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import OfferCreate


class TestOfferCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        offer = await sign_and_reliable_submission_async(
            OfferCreate(
                account=WALLET.classic_address,
                taker_gets="13100000",
                taker_pays=IssuedCurrencyAmount(
                    currency="USD",
                    issuer=WALLET.classic_address,
                    value="10",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(offer.is_successful())
