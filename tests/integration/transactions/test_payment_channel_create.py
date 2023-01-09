from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import DESTINATION, WALLET, GATEWAY
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import PaymentChannelCreate


class TestPaymentChannelCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_native_functionality(self, client):
        payment_channel = await submit_transaction_async(
            PaymentChannelCreate(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                amount="100",
                destination=DESTINATION.classic_address,
                settle_delay=86400,
                public_key=WALLET.public_key,
            ),
            WALLET,
        )
        self.assertTrue(payment_channel.is_successful())
        WALLET.sequence += 1

    @test_async_and_sync(globals())
    async def test_ic_functionality(self, client):
        payment_channel = await submit_transaction_async(
            PaymentChannelCreate(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                amount=IssuedCurrencyAmount(
                    currency="USD",
                    issuer=GATEWAY.classic_address,
                    value="100",
                ),
                destination=DESTINATION.classic_address,
                settle_delay=86400,
                public_key=WALLET.public_key,
            ),
            WALLET,
        )
        self.assertTrue(payment_channel.is_successful())
        WALLET.sequence += 1
