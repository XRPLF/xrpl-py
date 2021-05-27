try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountDelete

# We can re-use the shared wallet bc this test should fail to actually delete
# the associated account.
ACCOUNT = WALLET.classic_address

# AccountDelete transactions have a special fee.
# See https://xrpl.org/accountdelete.html#special-transaction-cost.
FEE = "5000000"
DESTINATION_TAG = 3


class TestAccountDelete(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        account_delete = AccountDelete(
            account=ACCOUNT,
            fee=FEE,
            sequence=WALLET.sequence,
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
        )
        response = await submit_transaction_async(
            account_delete, WALLET, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1

        # Note, we can't test the `engine_result` without waiting a significant
        # amount of time because accounts can't be deleted until some number of
        # ledgers have closed since its creation.
        #
        # The documentation for `tecTOO_SOON` reads:
        # "The AccountDelete transaction failed because the account to be deleted had a
        # Sequence number that is too high. The current ledger index must be at least
        # 256 higher than the account's sequence number."
        # self.assertEqual(response.result['engine_result'], 'tesSUCCESS')
