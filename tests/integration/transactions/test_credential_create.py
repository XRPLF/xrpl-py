import random

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.credential_create import CredentialCreate
from xrpl.utils import str_to_hex

_URI = "www.my-id.com/username"

# Use an arbitrary seed for reproducibility of tests
random.seed(42)


class TestCredentialCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_valid(self, client):
        tx = CredentialCreate(
            account=WALLET.address,
            subject=DESTINATION.address,
            # Disambiguate the sync/async, json/websocket tests with different
            # credential type values -- this avoids tecDUPLICATE error
            credential_type=str_to_hex("Passport_" + str(random.randint(0, 9))),
            uri=str_to_hex(_URI),
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
