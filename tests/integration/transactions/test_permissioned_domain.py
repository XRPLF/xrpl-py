from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import (  # CREDENTIAL_ACCEPT_RESPONSE,
    DESTINATION,
    WALLET,
)
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.requests.ledger_data import LedgerData
from xrpl.models.requests.ledger_entry import LedgerEntry, PermissionedDomain
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.credential_accept import CredentialAccept
from xrpl.models.transactions.credential_create import CredentialCreate
from xrpl.models.transactions.permissioned_domain_delete import PermissionedDomainDelete
from xrpl.models.transactions.permissioned_domain_set import (
    Credential,
    PermissionedDomainSet,
)
from xrpl.utils import str_to_hex


class TestPermissionedDomain(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_valid_pd_workflow(self, client):

        # Note: In the below test, WALLET is the "Issuer" of the said credential and is
        # also the "Owner" of the PermissionedDomain, but these roles need not be
        # fulfilled by the same account

        # Step-1a: Create a Credential object
        cred_type: str = str_to_hex("IdentityDocument")
        await sign_and_reliable_submission_async(
            CredentialCreate(
                account=WALLET.address,
                subject=DESTINATION.address,
                credential_type=cred_type,
            ),
            WALLET,
        )

        credential_accept_txn_response = await sign_and_reliable_submission_async(
            CredentialAccept(
                issuer=WALLET.address,
                credential_type=cred_type,
                account=DESTINATION.address,
            ),
            DESTINATION,
        )

        # Step-1b: Create a PermissionedDomain object
        response = await sign_and_reliable_submission_async(
            PermissionedDomainSet(
                account=WALLET.address,
                accepted_credentials=[
                    Credential(
                        credential_type=credential_accept_txn_response.result[
                            "tx_json"
                        ]["CredentialType"],
                        issuer=credential_accept_txn_response.result["tx_json"][
                            "Issuer"
                        ],
                    )
                ],
            ),
            WALLET,
            client,
        )

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-2: Verify the existence of the above PD ledger object through the RPC
        # calls -- ledger_entry, ledger_data, account_objects

        # Use the account_objects RPC to verify the creation of the PermissionedDomain
        # ledger object
        account_objects_response = await client.request(
            AccountObjects(
                account=WALLET.address, type=AccountObjectType.PERMISSIONED_DOMAIN
            )
        )
        self.assertEqual(account_objects_response.status, ResponseStatus.SUCCESS)

        # Use the LedgerEntry RPC to validate the creation of the credential object
        ledger_entry_response = await client.request(
            LedgerEntry(
                # Use the LedgerIndex from the account_objects RPC response
                permissioned_domain=account_objects_response.result["account_objects"][
                    0
                ]["index"]
            )
        )
        self.assertEqual(ledger_entry_response.status, ResponseStatus.SUCCESS)

        # Alternatively: Use the account and sequence-number to retrieve a
        # PermissionedDomain
        ledger_entry_response = await client.request(
            LedgerEntry(
                permissioned_domain=PermissionedDomain(
                    account=WALLET.address,
                    seq=account_objects_response.result["account_objects"][0][
                        "Sequence"
                    ],
                )
            )
        )

        self.assertEqual(ledger_entry_response.status, ResponseStatus.SUCCESS)

        # Use the ledger_data command to validate the creation of PermissionedDomain
        # object
        ledger_data_response = await client.request(
            LedgerData(ledger_index=response.result["validated_ledger_index"])
        )
        self.assertEqual(ledger_data_response.status, ResponseStatus.SUCCESS)

        # Step-3: Delete the PD object

        response = await sign_and_reliable_submission_async(
            PermissionedDomainDelete(
                account=WALLET.address,
                domain_id=ledger_entry_response.result["index"],
            ),
            WALLET,
            client,
        )

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Verify the PermissionedDomain object was deleted
        account_objects_response = await client.request(
            AccountObjects(
                account=WALLET.address, type=AccountObjectType.PERMISSIONED_DOMAIN
            )
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 0)
