from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import DESTINATION, FEE, WALLET
from xrpl.models.transactions import Payment


class TestPayment(TestCase):
    def test_basic_functionality(self):
        response = submit_transaction(
            Payment(
                account=WALLET.classic_address,
                sequence=WALLET.next_sequence_num,
                fee=FEE,
                amount="1",
                destination=DESTINATION.classic_address,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
