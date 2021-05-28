from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models.transactions import SetRegularKey
from xrpl.wallet import Wallet


class TestSetRegularKey(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        regular_key = Wallet.create().classic_address
        response = await submit_transaction_async(
            SetRegularKey(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                regular_key=regular_key,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
