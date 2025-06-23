from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import (
    AccountSet,
    AccountSetAsfFlag,
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
from xrpl.models.requests import AccountObjects, LedgerEntry
from xrpl.models.requests.account_objects import AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.vault_create import WithdrawalPolicy
from xrpl.utils import str_to_hex
from xrpl.wallet import Wallet


class TestSingleAssetVault(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_sav_lifecycle(self, client):

        vault_owner = Wallet.create()
        await fund_wallet_async(vault_owner)

        issuer_wallet = Wallet.create()
        await fund_wallet_async(issuer_wallet)

        # Set up the relevant flags on the issuer_wallet account -- This is
        # a pre-requisite for a Vault to hold the Issued Currency Asset
        # This test uses an IOU to demonstrate the VaultClawback functionality.
        # Clawback is not possible with the native XRP asset.
        response = await sign_and_reliable_submission_async(
            AccountSet(
                account=issuer_wallet.classic_address,
                set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE,
            ),
            issuer_wallet,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        response = await sign_and_reliable_submission_async(
            AccountSet(
                account=issuer_wallet.classic_address,
                set_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
            ),
            issuer_wallet,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

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

        # Step-1.a: Create a vault
        tx = VaultCreate(
            account=vault_owner.address,
            asset=IssuedCurrency(currency="USD", issuer=issuer_wallet.address),
            assets_maximum="1000",
            withdrawal_policy=WithdrawalPolicy.VAULT_STRATEGY_FIRST_COME_FIRST_SERVE,
        )
        response = await sign_and_reliable_submission_async(tx, vault_owner, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-1.b: Verify the existence of the vault with account_objects RPC call
        account_objects_response = await client.request(
            AccountObjects(account=vault_owner.address, type=AccountObjectType.VAULT)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)

        VAULT_ID = account_objects_response.result["account_objects"][0]["index"]

        # Step-1.c: Verify the existence of the vault with ledger_entry RPC call
        ledger_entry_response = await client.request(LedgerEntry(index=VAULT_ID))
        self.assertEqual(ledger_entry_response.status, ResponseStatus.SUCCESS)

        # Step-2: Update the characteristics of the vault with VaultSet transaction
        # print(await client.request(AccountInfo(account=vault_owner.address)))
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

    @test_async_and_sync(globals())
    async def test_encoding_non_hex_data_field(self, client):

        vault_owner = Wallet.create()
        await fund_wallet_async(vault_owner)

        issuer_wallet = Wallet.create()
        await fund_wallet_async(issuer_wallet)
        tx = VaultCreate(
            account=vault_owner.address,
            asset=IssuedCurrency(currency="USD", issuer=issuer_wallet.address),
            assets_maximum="1000",
            withdrawal_policy=WithdrawalPolicy.VAULT_STRATEGY_FIRST_COME_FIRST_SERVE,
            data="z",
        )
        response = await sign_and_reliable_submission_async(tx, vault_owner, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
