from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import AccountObjects, AccountObjectType, DIDSet
from xrpl.models.response import ResponseStatus

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
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm that the DID was actually created
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.DID)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
