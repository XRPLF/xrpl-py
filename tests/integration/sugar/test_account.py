try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import (
    JSON_RPC_CLIENT,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.asyncio.account import (
    does_account_exist,
    get_account_info,
    get_account_transactions,
    get_balance,
    get_latest_transaction,
)
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.models.transactions import Payment
from xrpl.wallet import Wallet, generate_faucet_wallet

NEW_WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)
EMPTY_WALLET = Wallet.create()


class TestAccount(IsolatedAsyncioTestCase):
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
            1000000000,
        )

    @test_async_and_sync(globals(), ["xrpl.account.get_account_transactions"])
    async def test_get_account_transactions(self, client):
        transactions = await get_account_transactions(
            NEW_WALLET.classic_address, client
        )
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["tx"]["TransactionType"], "Payment")
        self.assertEqual(transactions[0]["tx"]["Amount"], "1000000000")

    @test_async_and_sync(globals(), ["xrpl.account.get_account_transactions"])
    async def test_get_account_transactions_empty(self, client):
        transactions = await get_account_transactions(
            EMPTY_WALLET.classic_address, client
        )
        self.assertEqual(len(transactions), 0)

    @test_async_and_sync(globals(), ["xrpl.account.get_account_transactions"])
    async def test_payment_transactions(self, client):
        transactions = await get_account_transactions(
            NEW_WALLET.classic_address, client
        )
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["tx"]["TransactionType"], "Payment")
        self.assertEqual(transactions[0]["tx"]["Amount"], "1000000000")

    @test_async_and_sync(globals(), ["xrpl.account.get_account_transactions"])
    async def test_payment_transactions_xaddress(self, client):
        xaddress = classic_address_to_xaddress(NEW_WALLET.classic_address, None, True)
        transactions = await get_account_transactions(xaddress, client)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["tx"]["TransactionType"], "Payment")
        self.assertEqual(transactions[0]["tx"]["Amount"], "1000000000")

    @test_async_and_sync(globals(), ["xrpl.account.get_latest_transaction"])
    async def test_get_latest_transaction(self, client):
        # NOTE: this test may take a long time to run
        amount = "21000000"
        payment = Payment(
            account=WALLET.classic_address,
            destination=DESTINATION.classic_address,
            amount=amount,
        )
        await sign_and_reliable_submission_async(payment, WALLET)
        WALLET.sequence += 1

        response = await get_latest_transaction(WALLET.classic_address, client)
        self.assertEqual(len(response.result["transactions"]), 1)
        transaction = response.result["transactions"][0]["tx"]
        self.assertEqual(transaction["TransactionType"], "Payment")
        self.assertEqual(transaction["Amount"], amount)
        self.assertEqual(transaction["Account"], WALLET.classic_address)

    @test_async_and_sync(globals(), ["xrpl.account.get_account_info"])
    async def test_get_account_info(self, client):
        response = await get_account_info(WALLET.classic_address, client)
        self.assertTrue(response.is_successful())
        self.assertEqual(
            response.result["account_data"]["Account"],
            WALLET.classic_address,
        )
