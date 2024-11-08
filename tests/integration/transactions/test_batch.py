from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models import Batch, BatchFlag, Payment
from xrpl.models.response import ResponseStatus


class TestBatch(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        payment = Payment(
            account=WALLET.address,
            amount="1",
            destination=DESTINATION.address,
        )
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[payment, payment],
        )
        response = await sign_and_reliable_submission_async(batch, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
