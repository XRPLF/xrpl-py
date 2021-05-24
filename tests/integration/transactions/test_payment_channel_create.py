from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async
from tests.integration.reusable_values import DESTINATION, PAYMENT_CHANNEL, WALLET
from xrpl.models.transactions import PaymentChannelCreate


class TestPaymentChannelCreate(IsolatedAsyncioTestCase):
    def test_basic_functionality(self):
        # we're already requiring this elsewhere
        self.assertTrue(PAYMENT_CHANNEL.is_successful())

    async def test_basic_functionality_async(self):
        payment_channel = await submit_transaction_async(
            PaymentChannelCreate(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                amount="1",
                destination=DESTINATION.classic_address,
                settle_delay=86400,
                public_key=WALLET.public_key,
            ),
            WALLET,
        )
        self.assertTrue(payment_channel.is_successful())
        WALLET.sequence += 1
