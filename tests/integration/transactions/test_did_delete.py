from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import AccountObjects, AccountObjectType, DIDDelete, DIDSet
from xrpl.models.response import ResponseStatus

_VALID_FIELD = "1234567890abcdefABCDEF"


class TestDIDDelete(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic(self, client):
        # Create DID to delete
        setup_tx = DIDSet(
            account=WALLET.address,
            did_document=_VALID_FIELD,
            uri=_VALID_FIELD,
            data=_VALID_FIELD,
        )
        response = await sign_and_reliable_submission_async(setup_tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm that the DID was actually created
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.DID)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)

        # Create DID to delete
        tx = DIDDelete(
            account=WALLET.address,
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm that the DID was actually deleted
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.DID)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 0)
