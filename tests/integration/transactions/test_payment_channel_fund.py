from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.models.transactions import PaymentChannelFund

FEE = "3000000"


class TestPaymentChannelFund(TestCase):
    def test_basic_functionality(self):
        response = submit_transaction(
            PaymentChannelFund(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                channel=PAYMENT_CHANNEL.result["hash"],
                amount="1",
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())

    def test_high_fee_authorized(self):
        # GIVEN a new PaymentChannelFund transaction
        response = submit_transaction(
            # GIVEN a new PaymentChannelFund transaction
            PaymentChannelFund(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                channel=PAYMENT_CHANNEL.result["hash"],
                amount="1",
                # WITH the fee higher than 2 XRP
                fee=FEE,
            ),
            WALLET,
            # WITHOUT checking the fee value
            check_fee=False,
        )
        # THEN we expect a successful response
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
