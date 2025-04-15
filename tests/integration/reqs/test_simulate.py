from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models import AccountSet, Simulate


class TestSimulate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
            Simulate(transaction=AccountSet(account=WALLET.classic_address))
        )

        self.assertEqual(response.type, "response")
        self.assertIn(
            "meta", response.result, "Key 'meta' not found in simulate response."
        )
        self.assertIsInstance(
            response.result["meta"], dict, "'meta' should be a dictionary."
        )
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        self.assertEqual(response.result["engine_result_code"], 0)
        self.assertFalse(response.result["applied"])
