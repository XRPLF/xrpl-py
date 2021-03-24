from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.models.transactions import PaymentChannelClaim


class TestPaymentChannelClaim(TestCase):
    def test_reciever_claim(self):
        response = submit_transaction(
            PaymentChannelClaim(
                account=WALLET.classic_address,
                sequence=WALLET.next_sequence_num,
                channel=PAYMENT_CHANNEL.result["hash"],
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.next_sequence_num += 1
