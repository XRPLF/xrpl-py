from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    FUNDING_AMOUNT,
    fund_wallet,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.asyncio.account import does_account_exist, get_balance, get_latest_transaction
from xrpl.asyncio.clients.exceptions import XRPLRequestFailureException
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.models.transactions import Payment
from xrpl.wallet import Wallet

NEW_WALLET = Wallet.create()
fund_wallet(NEW_WALLET)
EMPTY_WALLET = Wallet.create()


class TestAccount(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.does_account_exist"])
    async def test_does_account_exist_true(self, client):
        self.assertTrue(await does_account_exist(WALLET.address, client))

    @test_async_and_sync(globals(), ["xrpl.account.does_account_exist"])
    async def test_does_account_exist_false(self, client):
        address = Wallet.create().classic_address
        self.assertFalse(await does_account_exist(address, client))

    @test_async_and_sync(globals(), ["xrpl.account.does_account_exist"])
    async def test_does_account_exist_throws_for_invalid_account(self, client):
        address = "a"
        with self.assertRaises(XRPLRequestFailureException):
            await does_account_exist(address, client)

    @test_async_and_sync(globals(), ["xrpl.account.does_account_exist"])
    async def test_does_account_exist_xaddress(self, client):
        xaddress = classic_address_to_xaddress(WALLET.address, None, True)
        self.assertTrue(await does_account_exist(xaddress, client))

    @test_async_and_sync(globals(), ["xrpl.account.get_balance"])
    async def test_get_balance(self, client):
        self.assertEqual(
            await get_balance(NEW_WALLET.address, client),
            int(FUNDING_AMOUNT),
        )

    @test_async_and_sync(globals(), ["xrpl.account.get_latest_transaction"])
    async def test_get_latest_transaction(self, client):
        # NOTE: this test may take a long time to run
        amount = "21000000"
        payment = Payment(
            account=WALLET.address,
            destination=DESTINATION.address,
            amount=amount,
        )
        await sign_and_reliable_submission_async(payment, WALLET, client)

        response = await get_latest_transaction(WALLET.address, client)
        self.assertEqual(len(response.result["transactions"]), 1)
        transaction = response.result["transactions"][0]["tx_json"]
        self.assertEqual(transaction["TransactionType"], "Payment")
        self.assertEqual(transaction["DeliverMax"], amount)
        self.assertEqual(transaction["Account"], WALLET.address)
