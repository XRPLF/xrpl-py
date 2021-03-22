from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import FEE, PAYMENT_CHANNEL, WALLET
from xrpl.models.transactions import PaymentChannelFund


class TestPaymentChannelFund(TestCase):
    def test_basic_functionality(self):
        response = submit_transaction(
            PaymentChannelFund(
                account=WALLET.classic_address,
                sequence=WALLET.next_sequence_num,
                fee=FEE,
                channel=PAYMENT_CHANNEL.result["hash"],
                amount="1",
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
