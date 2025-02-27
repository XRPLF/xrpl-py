import time

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models import AccountObjects, AccountObjectType, OracleSet
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.oracle_set import PriceData
from xrpl.utils import str_to_hex
from xrpl.wallet import Wallet

_PROVIDER = str_to_hex("provider")
_ASSET_CLASS = str_to_hex("currency")
# int data-type can contain the max UINT64 value, without loss of precision
_MAX_ASSET_PRICE = int(18446744073709551615)


class TestSetOracle(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        oracle_owner_wallet = Wallet.create()
        await fund_wallet_async(oracle_owner_wallet)
        tx = OracleSet(
            account=oracle_owner_wallet.address,
            # if oracle_document_id is not modified, the (sync, async) +
            # (json, websocket) combination of integration tests will update the same
            # oracle object using identical "LastUpdateTime". Updates to an oracle must
            # be more recent than its previous LastUpdateTime
            # a unique value is obtained for each combination of test run within the
            # implementation of the test_async_and_sync decorator.
            oracle_document_id=self.value,
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
                # validate the serialization of maximum allowed AssetPrice field
                PriceData(
                    base_asset="BTC",
                    quote_asset="INR",
                    asset_price=_MAX_ASSET_PRICE,
                    scale=2,
                ),
            ],
        )
        response = await sign_and_reliable_submission_async(
            tx, oracle_owner_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm that the PriceOracle was actually created
        account_objects_response = await client.request(
            AccountObjects(
                account=oracle_owner_wallet.address, type=AccountObjectType.ORACLE
            )
        )

        # subsequent integration tests (sync/async + json/websocket) add one
        # oracle object to the account
        self.assertTrue(len(account_objects_response.result["account_objects"]) > 0)

        # The maximum AssetPrice value is stored as a `str` type in base-16 format
        self.assertTrue(
            account_objects_response.result["account_objects"][0]["PriceDataSeries"][2][
                "PriceData"
            ]["AssetPrice"],
            "ffffffffffffffff",
        )
