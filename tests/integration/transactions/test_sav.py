from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import (
    TrustSet,
    VaultCreate,
    VaultDelete,
    VaultDeposit,
    VaultSet,
    VaultWithdraw,
)
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.requests import AccountObjects
from xrpl.models.requests.account_objects import AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.utils import str_to_hex
from xrpl.wallet import Wallet


class TestSingleAssetVault(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_sav_lifecycle(self, client):

        vault_owner = Wallet.create()
        await fund_wallet_async(vault_owner)

        # # Prerequisites: Set up the IOU trust lines
        # tx = TrustSet(
        #     account=vault_owner.address,
        #     limit_amount=IssuedCurrencyAmount(
        #         currency="USD", issuer=WALLET.address, value="1000"
        #     ),
        # )
        # response = await sign_and_reliable_submission_async(tx, vault_owner, client)
        # self.assertEqual(response.status, ResponseStatus.SUCCESS)
        # self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-1: Create a vault
        tx = VaultCreate(
            account=vault_owner.address,
            asset=XRP(),
            # asset=IssuedCurrency(currency="USD", issuer=WALLET.address),
            # TODO: This throws a Number::normalize 1 exception in rippled, why ??
            # Possible errors in serialization of Number type
            # asset_maximum="1000",
        )
        response = await sign_and_reliable_submission_async(tx, vault_owner, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Verify the existence of the vault with account_objects RPC call
        account_objects_response = await client.request(
            AccountObjects(account=vault_owner.address, type=AccountObjectType.VAULT)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)

        VAULT_ID = account_objects_response.result["account_objects"][0]["index"]

        # Step-2: Update the characteristics of the vault with VaultSet transaction
        tx = VaultSet(
            account=vault_owner.address,
            vault_id=VAULT_ID,
            data=str_to_hex("auxilliary data pertaining to the vault"),
        )
        response = await sign_and_reliable_submission_async(tx, vault_owner, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-3: Execute a VaultDeposit transaction
        tx = VaultDeposit(
            account=WALLET.address,
            vault_id=VAULT_ID,
            amount="10",
            # amount=IssuedCurrencyAmount(
            #     currency="USD", issuer=WALLET.address, value="10"
            # ),
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Execute a VaultWithdraw transaction
        tx = VaultWithdraw(
            account=WALLET.address,
            vault_id=VAULT_ID,
            amount="10",
            # amount=IssuedCurrencyAmount(
            #     currency="USD", issuer=WALLET.address, value="10"
            # ),
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # TODO: Execute a VaultClawback transaction

        # Delete the Vault with VaultDelete transaction
        tx = VaultDelete(
            account=vault_owner.address,
            vault_id=account_objects_response.result["account_objects"][0]["index"],
        )
        response = await sign_and_reliable_submission_async(tx, vault_owner, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
