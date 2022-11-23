from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import OfferCreate


class TestOfferCreate(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_basic_functionality(self, client):
        offer = await submit_transaction_async(
            OfferCreate(
                account=WALLET.classic_address,
                sequence=await get_next_valid_seq_number(
                    WALLET.classic_address, client
                ),
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
