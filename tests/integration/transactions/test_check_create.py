from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import CheckCreate

ACCOUNT = WALLET.classic_address
DESTINATION_TAG = 1
SENDMAX = "100000000"
EXPIRATION = 970113521
INVOICE_ID = "6F1DFD1D0FE8A32E40E1F2C05CF1C15545BAB56B617F9C6C2D63A6B704BEF59B"


class TestCheckCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        check_create = CheckCreate(
            account=ACCOUNT,
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
            send_max=SENDMAX,
            expiration=EXPIRATION,
            invoice_id=INVOICE_ID,
        )
        response = await sign_and_reliable_submission_async(
            check_create, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
