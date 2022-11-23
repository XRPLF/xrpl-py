from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.models.transactions import Payment


class TestPayment(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_basic_functionality(self, client):
        response = await submit_transaction_async(
            Payment(
                account=WALLET.classic_address,
                sequence=await get_next_valid_seq_number(
                    WALLET.classic_address, client
                ),
                amount="1",
                destination=DESTINATION.classic_address,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
