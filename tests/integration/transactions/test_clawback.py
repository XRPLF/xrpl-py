from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import CLAWBACK_HOLDER, CLAWBACK_ISSUER
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import Clawback


class TestClawback(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await sign_and_reliable_submission_async(
            Clawback(
                account=CLAWBACK_ISSUER.classic_address,
                amount=IssuedCurrencyAmount(
                    issuer=CLAWBACK_HOLDER.classic_address,
                    currency="USD",
                    value="100",
                ),
            ),
            CLAWBACK_ISSUER,
            client,
        )
        self.assertTrue(response.is_successful())
