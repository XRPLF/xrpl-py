from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import AccountObjects, AccountObjectType, OracleDelete, OracleSet
from xrpl.models.response import ResponseStatus

_PROVIDER = "chainlink"
_ASSET_CLASS = "currency"


class TestDeleteOracle(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic(self, client):
        # Create PriceOracle to delete
        setup_tx = OracleSet(
            account=WALLET.address,
            oracle_document_id=1,
            provider=_PROVIDER,
            asset_class=_ASSET_CLASS,
        )
        response = await sign_and_reliable_submission_async(setup_tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm that the PriceOracle was actually created
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.ORACLE)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)

        # Create PriceOracle to delete
        tx = OracleDelete(
            account=WALLET.address,
            oracle_document_id=1,
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm that the PriceOracle was actually deleted
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.ORACLE)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 0)
