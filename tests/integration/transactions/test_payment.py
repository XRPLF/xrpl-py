from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.transactions import Payment

FEE = "3000000"


class TestPayment(TestCase):
    def test_basic_functionality(self):
        response = submit_transaction(
            Payment(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                amount="1",
                destination=DESTINATION.classic_address,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1

    def test_high_fee_authorized(self):
        # GIVEN a new Payment transaction
        response = submit_transaction(
            Payment(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                amount="1",
                # WITH the fee higher than 2 XRP
                fee=FEE,
                destination=DESTINATION.classic_address,
            ),
            WALLET,
            # WITHOUT checking the fee value
            check_fee=False,
        )
        # THEN we expect the transaction to be successful
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
