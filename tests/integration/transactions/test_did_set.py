from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DIDSet

_VALID_FIELD = "1234567890abcdefABCDEF"


class TestDIDSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        tx = DIDSet(
            account=WALLET.address,
            did_document=_VALID_FIELD,
            uri=_VALID_FIELD,
            data=_VALID_FIELD,
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
