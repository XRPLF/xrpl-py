from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountSet, Payment

DEV_JSON_RPC_URL = "https://s.devnet.rippletest.net:51234"
DEV_JSON_RPC_CLIENT = AsyncJsonRpcClient(DEV_JSON_RPC_URL)


class TestWallet(IsolatedAsyncioTestCase):
    async def test_generate_faucet_wallet_dev(self):
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

    async def test_generate_faucet_wallet_rel_sub(self):
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
