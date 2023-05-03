from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.transactions import Payment


class TestPayment(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await sign_and_reliable_submission_async(
            Payment(
                account=WALLET.classic_address,
                amount="1",
                destination=DESTINATION.classic_address,
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
