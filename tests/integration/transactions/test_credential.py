from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models import AccountObjects, AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.credential_accept import CredentialAccept
from xrpl.models.transactions.credential_create import CredentialCreate
from xrpl.models.transactions.credential_delete import CredentialDelete
from xrpl.utils import str_to_hex

_URI = "www.my-id.com/username"


def is_cred_object_present(result, issuer, subject, cred_type) -> bool:
    """
    Utility method that checks if the specified JSON contains the Credential ledger
    object. The result JSON must be the output of account_objects RPC command.

    Returns True, if the input JSON contains the Credential Ledger object
    Returns False, otherwise
    """

    for val in result["account_objects"]:
        if (
            val["Issuer"] == issuer
            and val["Subject"] == subject
            and val["CredentialType"] == cred_type
        ):
            return True

    return False


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

        # Note: If it isn't too cluttered, verification tests pertaining to the
        # existence of Credential ledger object on the Issuer's and Subject's directory
        # pages can be included here

        # Execute the CredentialAccept transaction on the above Credential ledger object
        tx = CredentialAccept(
            issuer=_ISSUER, account=_SUBJECT, credential_type=cred_type
        )
        # CredentialAccept transaction is submitted by SUBJECT
        response = await sign_and_reliable_submission_async(tx, DESTINATION, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Execute the CredentialDelete transaction
        # Subject initiates the deletion of the Credential ledger object
        tx = CredentialDelete(
            issuer=_ISSUER, account=_SUBJECT, credential_type=cred_type
        )

        response = await sign_and_reliable_submission_async(tx, DESTINATION, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # The credential ledger object must be deleted from both the Issuer and Subject
        # account's directory pages
        account_objects_response = await client.request(
            AccountObjects(account=_ISSUER, type=AccountObjectType.CREDENTIAL)
        )
        self.assertFalse(
            is_cred_object_present(
                account_objects_response.result,
                issuer=_ISSUER,
                subject=_SUBJECT,
                cred_type=cred_type,
            )
        )

        # Verify that the Credential object has been deleted from the Subject's
        # directory page as well
        account_objects_response = await client.request(
            AccountObjects(account=_SUBJECT, type=AccountObjectType.CREDENTIAL)
        )
        self.assertFalse(
            is_cred_object_present(
                account_objects_response.result,
                issuer=_ISSUER,
                subject=_SUBJECT,
                cred_type=cred_type,
            )
        )
