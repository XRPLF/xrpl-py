from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import CheckCancel

ACCOUNT = WALLET.classic_address

CHECK_ID = "49647F0D748DC3FE26BDACBC57F251AADEFFF391403EC9BF87C97F67E9977FB0"


class TestCheckCancel(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        check_cancel = CheckCancel(
            account=ACCOUNT,
            check_id=CHECK_ID,
        )
        response = await sign_and_reliable_submission_async(
            check_cancel, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        # This transaction shouldn't actually succeed, because this isn't a real check:
        # Docs for tecNO_ENTRY read:
        # "The transaction tried to modify a ledger object, such as a Check,
        # Payment Channel, or Deposit Preauthorization, but the specified object
        # does not exist. It may have already been deleted by a previous
        # transaction or the transaction may have an incorrect value in an
        # ID field such as CheckID, Channel, Unauthorize."
        self.assertEqual(response.result["engine_result"], "tecNO_ENTRY")
