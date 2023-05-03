from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.transactions import PaymentChannelCreate


class TestPaymentChannelCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        payment_channel = await sign_and_reliable_submission_async(
            PaymentChannelCreate(
                account=WALLET.classic_address,
                amount="1",
                destination=DESTINATION.classic_address,
                settle_delay=86400,
                public_key=WALLET.public_key,
            ),
            WALLET,
            client,
        )
        self.assertTrue(payment_channel.is_successful())
