from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.models.transactions import PaymentChannelClaim


class TestPaymentChannelClaim(TestCase):
    def test_receiver_claim(self):
        response = submit_transaction(
            PaymentChannelClaim(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                channel=PAYMENT_CHANNEL.result["hash"],
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
