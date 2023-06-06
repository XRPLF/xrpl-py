from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import CheckCash

ACCOUNT = WALLET.classic_address
CHECK_ID = "838766BA2B995C00744175F69A1B11E32C3DBC40E64801A4056FCBD657F57334"
AMOUNT = "100000000"
DELIVER_MIN = "100000000"


class TestCheckCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_required_fields_with_amount(self, client):
        check_cash = CheckCash(
            account=ACCOUNT,
            check_id=CHECK_ID,
            amount=AMOUNT,
        )
        response = await sign_and_reliable_submission_async(check_cash, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        # Getting `tecNO_ENTRY` codes because using a non-existent check ID
        self.assertEqual(response.result["engine_result"], "tecNO_ENTRY")

    @test_async_and_sync(globals())
    async def test_required_fields_with_deliver_min(self, client):
        check_cash = CheckCash(
            account=ACCOUNT,
            check_id=CHECK_ID,
            deliver_min=DELIVER_MIN,
        )
        response = await sign_and_reliable_submission_async(check_cash, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tecNO_ENTRY")
