from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.transactions import TicketCreate


class TestTicketCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await sign_and_reliable_submission_async(
            TicketCreate(
                account=WALLET.classic_address,
                ticket_count=2,
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
