from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction, submit_transaction_async
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.transactions import Payment


class TestPayment(IsolatedAsyncioTestCase):
    def test_basic_functionality_sync(self):
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

    async def test_basic_functionality_async(self):
        response = await submit_transaction_async(
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
