from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.credential_accept import CredentialAccept
from xrpl.models.transactions.credential_create import CredentialCreate
from xrpl.utils import str_to_hex

_URI = "www.my-id.com/username"


class TestCredentialCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_valid(self, client):
        # Define entities helpful for Credential lifecycle
        _ISSUER = WALLET.address
        _SUBJECT = DESTINATION.address

        # Disambiguate the sync/async, json/websocket tests with different
        # credential type values -- this avoids tecDUPLICATE error
        # self.value is defined inside the above decorator
        cred_type = str_to_hex("Passport_" + str(self.value))
        tx = CredentialCreate(
            account=_ISSUER,
            subject=_SUBJECT,
            credential_type=cred_type,
            uri=str_to_hex(_URI),
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Execute the CredentialAccept transaction on the above Credential ledger object
        tx = CredentialAccept(
            issuer=_ISSUER, account=_SUBJECT, credential_type=cred_type
        )
        # CredentialAccept transaction is submitted by SUBJECT
        response = await sign_and_reliable_submission_async(tx, DESTINATION, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
