from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.models.transactions import PaymentChannelFund


class TestPaymentChannelFund(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await sign_and_reliable_submission_async(
            PaymentChannelFund(
                account=WALLET.classic_address,
                channel=PAYMENT_CHANNEL.result["tx_json"]["hash"],
                amount="1",
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
