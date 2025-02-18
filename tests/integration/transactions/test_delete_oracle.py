import time

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models import AccountObjects, AccountObjectType, OracleDelete, OracleSet
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.oracle_set import PriceData
from xrpl.utils import str_to_hex
from xrpl.wallet import Wallet

_PROVIDER = str_to_hex("chainlink")
_ASSET_CLASS = str_to_hex("currency")


class TestDeleteOracle(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic(self, client):
        # Use a fresh wallet for OracleSet transactions. Re-using the WALLET and
        # DESTINATION variables could cause conflicts with other integration tests.
        oracle_owner_wallet = Wallet.create()
        await fund_wallet_async(oracle_owner_wallet)

        oracle_id = self.value

        # Create PriceOracle, to be deleted later
        tx = OracleSet(
            account=oracle_owner_wallet.address,
            # unlike the integration tests for OracleSet transaction, we do not have to
            # dynamically change the oracle_document_id for these integration tests.
            # This is because the Oracle LedgerObject is deleted by the end of the test.
            oracle_document_id=oracle_id,
            provider=_PROVIDER,
            asset_class=_ASSET_CLASS,
            last_update_time=int(time.time()),
            price_data_series=[
                PriceData(
                    base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                ),
                PriceData(
                    base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                ),
            ],
        )
        response = await sign_and_reliable_submission_async(
            tx, oracle_owner_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Create PriceOracle to delete
        tx = OracleDelete(
            account=oracle_owner_wallet.address,
            oracle_document_id=oracle_id,
        )
        response = await sign_and_reliable_submission_async(
            tx, oracle_owner_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm that the PriceOracle was actually deleted
        account_objects_response = await client.request(
            AccountObjects(
                account=oracle_owner_wallet.address, type=AccountObjectType.ORACLE
            )
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 0)
