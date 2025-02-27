from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import (
    Payment,
    TrustSet,
    VaultClawback,
    VaultCreate,
    VaultDelete,
    VaultDeposit,
    VaultSet,
    VaultWithdraw,
)
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.currencies import IssuedCurrency
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

        issuer_wallet = Wallet.create()
        await fund_wallet_async(issuer_wallet)

        # Step-0.a: Prerequisites: Set up the IOU trust line
        tx = TrustSet(
            account=WALLET.address,
            limit_amount=IssuedCurrencyAmount(
                currency="USD", issuer=issuer_wallet.address, value="1000"
            ),
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-0.b: Send the payment of IOUs from issuer_wallet to WALLET
        tx = Payment(
            account=issuer_wallet.address,
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=issuer_wallet.address, value="1000"
            ),
            destination=WALLET.address,
        )
        response = await sign_and_reliable_submission_async(tx, issuer_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-1: Create a vault
        tx = VaultCreate(
            account=vault_owner.address,
            asset=IssuedCurrency(currency="USD", issuer=issuer_wallet.address),
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
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=issuer_wallet.address, value="10"
            ),
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-4: Execute a VaultWithdraw transaction
        tx = VaultWithdraw(
            account=WALLET.address,
            vault_id=VAULT_ID,
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=issuer_wallet.address, value="9"
            ),
        )
        response = await sign_and_reliable_submission_async(tx, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-5: Execute a VaultClawback transaction from issuer_wallet
        tx = VaultClawback(
            holder=WALLET.address,
            account=issuer_wallet.address,
            vault_id=VAULT_ID,
            # Note: Although the amount is specified as 9, 1 unit of the IOU will be
            # clawed back, because that is the remaining balance in the vault
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=issuer_wallet.address, value="9"
            ),
        )
        response = await sign_and_reliable_submission_async(tx, issuer_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-6: Delete the Vault with VaultDelete transaction
        tx = VaultDelete(
            account=vault_owner.address,
            vault_id=VAULT_ID,
        )
        response = await sign_and_reliable_submission_async(tx, vault_owner, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
