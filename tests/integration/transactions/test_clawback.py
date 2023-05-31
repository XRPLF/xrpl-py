from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import Clawback


class TestClawback(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await submit_transaction_async(
            Clawback(
                account=WALLET.classic_address,
                amount=IssuedCurrencyAmount(
                    issuer=DESTINATION.classic_address,
                    currency="USD",
                    value="100",
                ),
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
