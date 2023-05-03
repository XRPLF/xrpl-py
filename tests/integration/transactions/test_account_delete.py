from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountDelete
from xrpl.utils import xrp_to_drops

# We can re-use the shared wallet bc this test should fail to actually delete
# the associated account.
ACCOUNT = WALLET.classic_address

# AccountDelete transactions have a special fee.
# See https://xrpl.org/accountdelete.html#special-transaction-cost.
FEE = xrp_to_drops(5)
DESTINATION_TAG = 3


class TestAccountDelete(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        account_delete = AccountDelete(
            account=ACCOUNT,
            fee=FEE,
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
        )
        response = await sign_and_reliable_submission_async(
            account_delete, WALLET, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

        # Note, we can't test the `engine_result` without waiting a significant
        # amount of time because accounts can't be deleted until some number of
        # ledgers have closed since its creation.
        #
        # The documentation for `tecTOO_SOON` reads:
        # "The AccountDelete transaction failed because the account to be deleted had a
        # Sequence number that is too high. The current ledger index must be at least
        # 256 higher than the account's sequence number."
        # self.assertEqual(response.result['engine_result'], 'tesSUCCESS')
