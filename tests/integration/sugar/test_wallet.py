import time
import asyncio
from threading import Thread

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.clients import AsyncJsonRpcClient, AsyncWebsocketClient
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.clients import JsonRpcClient, WebsocketClient
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.models.requests import AccountInfo
from xrpl.models.transactions import Payment
from xrpl.wallet import generate_faucet_wallet as sync_generate_faucet_wallet
from xrpl.wallet.main import Wallet

time_of_last_hooks_faucet_call = 0


def sync_generate_faucet_wallet_and_fund_again(self, client, faucet_host=None):
    wallet = sync_generate_faucet_wallet(client, faucet_host=faucet_host)
    result = client.request(
        AccountInfo(
            account=wallet.classic_address,
        ),
    )
    balance = int(result.result["account_data"]["Balance"])
    self.assertTrue(balance > 0)

    new_wallet = sync_generate_faucet_wallet(client, wallet, faucet_host=faucet_host)
    new_result = client.request(
        AccountInfo(
            account=new_wallet.classic_address,
        ),
    )
    new_balance = int(new_result.result["account_data"]["Balance"])
    self.assertTrue(new_balance > balance)


async def generate_faucet_wallet_and_fund_again(self, client, faucet_host=None):
    wallet = await generate_faucet_wallet(client, faucet_host=faucet_host)
    result = await client.request(
        AccountInfo(
            account=wallet.classic_address,
        ),
    )
    balance = int(result.result["account_data"]["Balance"])
    self.assertTrue(balance > 0)

    new_wallet = await generate_faucet_wallet(client, wallet, faucet_host=faucet_host)
    new_result = await client.request(
        AccountInfo(
            account=new_wallet.classic_address,
        ),
    )
    new_balance = int(new_result.result["account_data"]["Balance"])
    self.assertTrue(new_balance > balance)


class TestProcess(Thread):
    def __init__(self, testcase, test):
        Thread.__init__(self)
        self.testcase = testcase
        self.test = test

    def run(self):
        with self.testcase.subTest(method=self.test):
            method = getattr(TestWallet, self.test)
            asyncio.run(method(self.testcase))


class TestWallet(IntegrationTestCase):
    async def test_run_faucet_tests(self):
        def run_test(test_name):
            with self.subTest(method=test_name):
                method = getattr(TestWallet, test_name)
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method(self))
                else:
                    method(self)

        test_methods = [method for method in dir(self) if method.startswith("_test_")]

        processes = []
        for method in test_methods:
            process = Thread(target=run_test, args=(method,))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()

    async def _test_generate_faucet_wallet_rel_sub(self):
        async with AsyncWebsocketClient(
            "wss://s.altnet.rippletest.net:51233"
        ) as client:
            destination, wallet = await asyncio.gather(
                generate_faucet_wallet(client), generate_faucet_wallet(client)
            )
            response = await submit_transaction_async(
                Payment(
                    account=wallet.classic_address,
                    sequence=wallet.sequence,
                    fee="10",
                    amount="1",
                    destination=destination.classic_address,
                ),
                wallet,
                client=client,
            )
            self.assertTrue(response.is_successful())

    async def _test_generate_faucet_wallet_custom_host_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://xls20-sandbox.rippletest.net:51233"
        ) as client:
            await generate_faucet_wallet_and_fund_again(
                self, client, "faucet-nft.ripple.com"
            )

    async def _test_generate_faucet_wallet_custom_host_async_json_rpc(self):
        client = AsyncJsonRpcClient("http://xls20-sandbox.rippletest.net:51234")
        await generate_faucet_wallet_and_fund_again(
            self, client, "faucet-nft.ripple.com"
        )

    def _test_generate_faucet_wallet_custom_host_sync_websockets(self):
        with WebsocketClient("wss://xls20-sandbox.rippletest.net:51233") as client:
            sync_generate_faucet_wallet_and_fund_again(
                self, client, "faucet-nft.ripple.com"
            )

    def _test_generate_faucet_wallet_custom_host_sync_json_rpc(self):
        client = JsonRpcClient("http://xls20-sandbox.rippletest.net:51234")
        sync_generate_faucet_wallet_and_fund_again(
            self, client, "faucet-nft.ripple.com"
        )

    async def _test_generate_faucet_wallet_testnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://s.altnet.rippletest.net:51233"
        ) as client:
            await generate_faucet_wallet_and_fund_again(self, client)

    async def _test_generate_faucet_wallet_devnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://s.devnet.rippletest.net:51233"
        ) as client:
            await generate_faucet_wallet_and_fund_again(self, client)

    async def _test_generate_faucet_wallet_nft_devnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "ws://xls20-sandbox.rippletest.net:51233"
        ) as client:
            await generate_faucet_wallet_and_fund_again(self, client)

    async def _test_generate_faucet_wallet_hooks_v2_testnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://hooks-testnet-v2.xrpl-labs.com"
        ) as client:
            global time_of_last_hooks_faucet_call
            # Wait at least 10 seconds since last call to hooks v2 testnet faucet
            time_since_last_hooks_call = time.time() - time_of_last_hooks_faucet_call
            if time_since_last_hooks_call < 10:
                await asyncio.sleep(11 - time_since_last_hooks_call)

            wallet = await generate_faucet_wallet(client)
            time_of_last_hooks_faucet_call = time.time()

            result = await client.request(
                AccountInfo(
                    account=wallet.classic_address,
                ),
            )
            balance = int(result.result["account_data"]["Balance"])
            self.assertTrue(balance > 0)

    # Named different from test_generate_faucet_wallet_hooks_v2_testnet_async_websockets
    # so the test runs far from each other since hooks v2 testnet faucet
    # requires 10 seconds between calls
    async def _test_fund_given_wallet_hooks_v2_testnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://hooks-testnet-v2.xrpl-labs.com"
        ) as client:
            global time_of_last_hooks_faucet_call
            wallet = Wallet("sEdSigMti9uJFCnrkwsB3LJRGkVZHVA", 0)
            result = await client.request(
                AccountInfo(
                    account=wallet.classic_address,
                ),
            )
            balance = int(result.result["account_data"]["Balance"])

            # Wait at least 10 seconds since last call to hooks v2 testnet faucet
            time_since_last_hooks_call = time.time() - time_of_last_hooks_faucet_call
            if time_since_last_hooks_call < 10:
                await asyncio.sleep(11 - time_since_last_hooks_call)
            time_of_last_hooks_faucet_call = time.time()

            new_wallet = await generate_faucet_wallet(client, wallet)
            new_result = await client.request(
                AccountInfo(
                    account=new_wallet.classic_address,
                ),
            )
            new_balance = int(new_result.result["account_data"]["Balance"])
            self.assertTrue(new_balance > balance)

    def _test_wallet_get_xaddress(self):
        expected = classic_address_to_xaddress(WALLET.classic_address, None, False)
        self.assertEqual(WALLET.get_xaddress(), expected)
