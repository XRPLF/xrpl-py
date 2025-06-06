from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.asyncio.transaction import autofill
from xrpl.models import Batch, BatchFlag, Payment
from xrpl.models.response import ResponseStatus
from xrpl.transaction.batch_signers import sign_multiaccount_batch


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

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_multisign(self, client):
        payment = Payment(
            account=WALLET.address,
            amount="1",
            destination=DESTINATION.address,
        )
        payment2 = Payment(
            account=DESTINATION.address,
            amount="1",
            destination=WALLET.address,
        )
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[payment, payment2],
        )
        autofilled = await autofill(batch, client, 1)
        signed = sign_multiaccount_batch(DESTINATION, autofilled)
        response = await sign_and_reliable_submission_async(signed, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
