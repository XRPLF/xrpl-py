from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction, submit_transaction_async
from tests.integration.reusable_values import WALLET
from xrpl.models.transactions import SetRegularKey
from xrpl.wallet import Wallet


class TestSetRegularKey(IsolatedAsyncioTestCase):
    def test_all_fields_sync(self):
        regular_key = Wallet.create().classic_address
        response = submit_transaction(
            SetRegularKey(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                regular_key=regular_key,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1

    async def test_all_fields_async(self):
        regular_key = Wallet.create().classic_address
        response = await submit_transaction_async(
            SetRegularKey(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                regular_key=regular_key,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
