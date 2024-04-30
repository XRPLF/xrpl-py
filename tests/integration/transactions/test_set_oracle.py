import time

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import AccountObjects, AccountObjectType, OracleSet
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.set_oracle import PriceData
from xrpl.utils import str_to_hex

_PROVIDER = str_to_hex("provider")
_ASSET_CLASS = str_to_hex("currency")


class TestSetOracle(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        tx = OracleSet(
            account=WALLET.address,
            oracle_document_id=1,
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
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm that the PriceOracle was actually created
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.ORACLE)
        )

        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
