from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    FUNDING_AMOUNT,
    fund_wallet_sync,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.asyncio.account import does_account_exist, get_balance, get_latest_transaction
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.models.transactions import Payment
from xrpl.wallet import Wallet

NEW_WALLET = Wallet.create()
fund_wallet_sync(NEW_WALLET)
EMPTY_WALLET = Wallet.create()


class TestAccount(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.does_account_exist"])
    async def test_does_account_exist_true(self, client):
        self.assertTrue(await does_account_exist(WALLET.classic_address, client))

    @test_async_and_sync(globals(), ["xrpl.account.does_account_exist"])
    async def test_does_account_exist_false(self, client):
        address = "rG1QQv2nh2gr7RCZ1P8YYcBUcCCN633jCn"
        self.assertFalse(await does_account_exist(address, client))

    @test_async_and_sync(globals(), ["xrpl.account.does_account_exist"])
    async def test_does_account_exist_xaddress(self, client):
        xaddress = classic_address_to_xaddress(WALLET.classic_address, None, True)
        self.assertTrue(await does_account_exist(xaddress, client))

    @test_async_and_sync(globals(), ["xrpl.account.get_balance"])
    async def test_get_balance(self, client):
        self.assertEqual(
            await get_balance(NEW_WALLET.classic_address, client),
            int(FUNDING_AMOUNT),
        )

    @test_async_and_sync(globals(), ["xrpl.account.get_latest_transaction"])
    async def test_get_latest_transaction(self, client):
        # NOTE: this test may take a long time to run
        amount = "21000000"
        payment = Payment(
            account=WALLET.classic_address,
            destination=DESTINATION.classic_address,
            amount=amount,
        )
        await sign_and_reliable_submission_async(payment, WALLET, client)

        response = await get_latest_transaction(WALLET.classic_address, client)
        self.assertEqual(len(response.result["transactions"]), 1)
        transaction = response.result["transactions"][0]["tx"]
        self.assertEqual(transaction["TransactionType"], "Payment")
        self.assertEqual(transaction["Amount"], amount)
        self.assertEqual(transaction["Account"], WALLET.classic_address)
