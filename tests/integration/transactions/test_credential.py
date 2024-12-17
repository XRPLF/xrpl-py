from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models import AccountObjects, AccountObjectType
from xrpl.models.requests.ledger_entry import Credential, LedgerEntry
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.credential_accept import CredentialAccept
from xrpl.models.transactions.credential_create import CredentialCreate
from xrpl.models.transactions.credential_delete import CredentialDelete
from xrpl.utils import str_to_hex

_URI = "www.my-id.com/username"


def is_cred_object_present(
    result: dict, issuer: str, subject: str, cred_type: str
) -> bool:
    """
    Args:
        result: JSON response from account_objects RPC
        issuer: Address of the credential issuer
        subject: Address of the credential subject
        cred_type: Type of the credential

    Returns:
        bool: True if credential exists, False otherwise
    """

    for val in result["account_objects"]:
        if (
            val["Issuer"] == issuer
            and val["Subject"] == subject
            and val["CredentialType"] == cred_type
        ):
            return True

    return False


class TestCredentials(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_valid(self, client):
        # Define entities helpful for Credential lifecycle
        _ISSUER = WALLET.address
        _SUBJECT = DESTINATION.address
        _SUBJECT_WALLET = DESTINATION

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

        # Use the LedgerEntry RPC to validate the creation of the credential object
        ledger_entry_response = await client.request(
            LedgerEntry(
                credential=Credential(
                    subject=_SUBJECT, issuer=_ISSUER, credential_type=cred_type
                )
            )
        )

        self.assertEqual(ledger_entry_response.status, ResponseStatus.SUCCESS)

        # Execute the CredentialAccept transaction on the above Credential ledger object
        tx = CredentialAccept(
            issuer=_ISSUER, account=_SUBJECT, credential_type=cred_type
        )
        # CredentialAccept transaction is submitted by SUBJECT
        response = await sign_and_reliable_submission_async(tx, _SUBJECT_WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Execute the CredentialDelete transaction
        # Subject initiates the deletion of the Credential ledger object
        tx = CredentialDelete(
            issuer=_ISSUER, account=_SUBJECT, credential_type=cred_type
        )

        response = await sign_and_reliable_submission_async(tx, _SUBJECT_WALLET, client)
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
