from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.models.transactions import SetRegularKey
from xrpl.wallet import Wallet


class TestSetRegularKey(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_all_fields(self, client):
        regular_key = Wallet.generate().classic_address
        response = await submit_transaction_async(
            SetRegularKey(
                account=WALLET.classic_address,
                sequence=await get_next_valid_seq_number(
                    WALLET.classic_address, client
                ),
                regular_key=regular_key,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
