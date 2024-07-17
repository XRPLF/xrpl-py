from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models.requests import AccountTx


class TestAccountTx(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
            AccountTx(
                account=WALLET.address,
            )
        )
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_api_v2(self, client):
        response = await client.request(
            AccountTx(account=WALLET.address, api_version=2)
        )

        # use the below proxies to ensure that the correct API response is returned
        # API v2 returns tx_json field
        self.assertIn("tx_json", response.result["transactions"][0])

        # API v2 does not return a tx field
        self.assertNotIn("tx", response.result["transactions"][0])
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_api_v1(self, client):
        response = await client.request(
            AccountTx(account=WALLET.address, api_version=1)
        )

        # use the below proxies to ensure that the correct API response is returned
        # API v1 does not contain a tx_json field
        self.assertNotIn("tx_json", response.result["transactions"][0])

        # API v1 returns a tx field
        self.assertIn("tx", response.result["transactions"][0])
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_no_explicit_api_version(self, client):
        response_without_version = await client.request(
            AccountTx(account=WALLET.address)
        )

        response_with_version = await client.request(
            AccountTx(account=WALLET.address, api_version=2)
        )

        # if api_version is not explicitly specified, xrpl-py inserts api_version:2
        # inside the Requests
        self.assertEqual(response_with_version.result, response_without_version.result)
