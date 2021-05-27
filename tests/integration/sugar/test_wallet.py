try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import (
    retry,
    submit_transaction_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountSet, Payment

DEV_JSON_RPC_URL = "https://s.devnet.rippletest.net:51234"
DEV_JSON_RPC_CLIENT = AsyncJsonRpcClient(DEV_JSON_RPC_URL)


class TestWallet(IsolatedAsyncioTestCase):
    @retry
    @test_async_and_sync(globals(), ["xrpl.wallet.generate_faucet_wallet"], True)
    async def test_generate_faucet_wallet_dev(self, client):
        wallet = await generate_faucet_wallet(DEV_JSON_RPC_CLIENT)
        account_set = AccountSet(
            account=wallet.classic_address,
            fee="10",
            sequence=wallet.sequence,
            set_flag=3,
        )
        response = await submit_transaction_async(
            account_set, wallet, client=DEV_JSON_RPC_CLIENT
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @retry
    @test_async_and_sync(globals(), ["xrpl.wallet.generate_faucet_wallet"])
    async def test_generate_faucet_wallet_rel_sub(self, client):
        destination = await generate_faucet_wallet(DEV_JSON_RPC_CLIENT)
        wallet = await generate_faucet_wallet(DEV_JSON_RPC_CLIENT)
        response = await submit_transaction_async(
            Payment(
                account=wallet.classic_address,
                sequence=wallet.sequence,
                fee="10",
                amount="1",
                destination=destination.classic_address,
            ),
            wallet,
            client=DEV_JSON_RPC_CLIENT,
        )
        self.assertTrue(response.is_successful())

    def test_wallet_get_xaddress(self):
        expected = classic_address_to_xaddress(WALLET.classic_address, None, False)
        self.assertEqual(WALLET.get_xaddress(), expected)
