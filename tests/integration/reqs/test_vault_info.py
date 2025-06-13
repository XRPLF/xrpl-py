from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.currencies import XRP
from xrpl.models.requests import AccountObjects, VaultInfo
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import VaultCreate
from xrpl.models.transactions.vault_create import VaultCreateFlag
from xrpl.wallet import Wallet


class TestVaultInfo(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):

        VAULT_OWNER = Wallet.create()
        await fund_wallet_async(VAULT_OWNER)

        # Create a vault
        # Additionally validate the usage of flags in the VaultCreate transaction
        tx = VaultCreate(
            account=VAULT_OWNER.address,
            asset=XRP(),
            withdrawal_policy=1,
            flags=VaultCreateFlag.TF_VAULT_PRIVATE
            | VaultCreateFlag.TF_VAULT_SHARE_NON_TRANSFERABLE,
        )
        response = await sign_and_reliable_submission_async(tx, VAULT_OWNER, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Note: Due to the setup of the integration testing framework, it is difficult
        # to obtain the next-sequence number of an account (in sync Client tests).
        # Hence, AccountObjects request is used to fetch the `index` of the vault
        # ledger-object.
        vault_object = await client.request(
            AccountObjects(
                account=VAULT_OWNER.address,
                type="vault",
            )
        )
        self.assertEqual(len(vault_object.result["account_objects"]), 1)
        self.assertEqual(
            vault_object.result["account_objects"][0]["LedgerEntryType"], "Vault"
        )
        vault_object_hash = vault_object.result["account_objects"][0]["index"]

        # Fetch information about the vault using VaultInfo request
        response = await client.request(
            VaultInfo(
                vault_id=vault_object_hash,
            )
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["vault"]["Owner"], VAULT_OWNER.address)
        self.assertEqual(response.result["vault"]["index"], vault_object_hash)
