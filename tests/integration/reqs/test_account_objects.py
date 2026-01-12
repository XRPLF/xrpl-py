from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models.requests import AccountObjects


class TestAccountObjects(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
            AccountObjects(
                account=WALLET.address,
            )
        )
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_type_filter(self, client):
        response = await client.request(
            AccountObjects(
                account=WALLET.address,
                type="Escrow",
            )
        )
        self.assertTrue(response.is_successful())
        self.assertIsNotNone(response.result["account_objects"])

        # test case-insensitive type filter
        response = await client.request(
            AccountObjects(
                account=WALLET.address,
                type="mPtOkeNisSuance",
            )
        )
        self.assertTrue(response.is_successful())
        self.assertIsNotNone(response.result["account_objects"])
