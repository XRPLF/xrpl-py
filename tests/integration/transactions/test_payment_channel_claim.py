from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.models.transactions import PaymentChannelClaim

FEE = "3000000"


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

    def test_receiver_claim_with_high_fee_authorized(self):
        # GIVEN a new PaymentChannelClaim transaction
        response = submit_transaction(
            PaymentChannelClaim(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                # WITH the fee higher than 2 XRP
                fee=FEE,
                channel=PAYMENT_CHANNEL.result["hash"],
            ),
            WALLET,
            # WITHOUT checking the fee value
            check_fee=False,
        )
        # THEN we expect a successful response
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
