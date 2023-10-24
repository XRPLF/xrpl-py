import asyncio
import time
from threading import Thread

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async
from xrpl.asyncio.clients import AsyncJsonRpcClient, AsyncWebsocketClient
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.clients import JsonRpcClient, WebsocketClient
from xrpl.core.addresscodec.main import classic_address_to_xaddress
from xrpl.models.requests import AccountInfo
from xrpl.models.transactions import Payment
from xrpl.wallet import generate_faucet_wallet as sync_generate_faucet_wallet
from xrpl.wallet.main import Wallet

time_of_last_hooks_faucet_call = 0


def sync_generate_faucet_wallet_and_fund_again(
    self, client, faucet_host=None, usage_context="integration_test"
):
    wallet = sync_generate_faucet_wallet(
        client, faucet_host=faucet_host, usage_context=usage_context
    )
    result = client.request(
        AccountInfo(
            account=wallet.address,
        ),
    )
    balance = int(result.result["account_data"]["Balance"])
    self.assertTrue(balance > 0)

    new_wallet = sync_generate_faucet_wallet(
        client, wallet, faucet_host=faucet_host, usage_context="integration_test"
    )
    new_result = client.request(
        AccountInfo(
            account=new_wallet.address,
        ),
    )
    new_balance = int(new_result.result["account_data"]["Balance"])
    self.assertTrue(new_balance > balance)


async def generate_faucet_wallet_and_fund_again(
    self, client, faucet_host=None, usage_context="integration_test"
):
    wallet = await generate_faucet_wallet(
        client, faucet_host=faucet_host, usage_context=usage_context
    )
    result = await client.request(
        AccountInfo(
            account=wallet.address,
        ),
    )
    balance = int(result.result["account_data"]["Balance"])
    self.assertTrue(balance > 0)

    new_wallet = await generate_faucet_wallet(
        client, wallet, faucet_host=faucet_host, usage_context=usage_context
    )
    new_result = await client.request(
        AccountInfo(
            account=new_wallet.address,
        ),
    )
    new_balance = int(new_result.result["account_data"]["Balance"])
    self.assertTrue(new_balance > balance)


class TestWallet(IntegrationTestCase):
    async def test_run_faucet_tests(self):
        # run all the tests that start with `_test_` in parallel
        def run_test(test_name):
            with self.subTest(method=test_name):
                method = getattr(self, test_name)  # get the test with the given name
                if asyncio.iscoroutinefunction(method):  # is async
                    asyncio.run(method())
                else:  # is sync
                    method()

        # get all the test methods starting with `_parallel_test_`
        # (the ones to run in parallel)
        test_methods = [
            method for method in dir(self) if method.startswith("_parallel_test_")
        ]

        # run all the tests in parallel
        processes = []
        for method in test_methods:
            process = Thread(target=run_test, args=(method,))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()

    # ensure that the wallet creation has been validated and the account actually exists
    async def _parallel_test_generate_faucet_wallet_rel_sub(self):
        client = JsonRpcClient("https://s.devnet.rippletest.net:51234")
        destination = await generate_faucet_wallet(client)
        wallet = await generate_faucet_wallet(client)
        # TODO: refactor so this actually waits for validation
        response = await submit_transaction_async(
            Payment(
                account=wallet.address,
                fee="10",
                amount="1",
                destination=destination.address,
            ),
            wallet,
            client=client,
        )
        self.assertTrue(response.is_successful())

    # Custom host tests

    async def _parallel_test_generate_faucet_wallet_custom_host_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://s.devnet.rippletest.net:51233"
        ) as client:
            await generate_faucet_wallet_and_fund_again(
                self,
                client,
                "faucet.devnet.rippletest.net",
                usage_context="integration_test",
            )

    async def _parallel_test_generate_faucet_wallet_custom_host_async_json_rpc(self):
        client = AsyncJsonRpcClient("https://s.devnet.rippletest.net:51234")
        await generate_faucet_wallet_and_fund_again(
            self,
            client,
            "faucet.devnet.rippletest.net",
            usage_context="integration_test",
        )

    def _parallel_test_generate_faucet_wallet_custom_host_sync_websockets(self):
        with WebsocketClient("wss://s.devnet.rippletest.net:51233") as client:
            sync_generate_faucet_wallet_and_fund_again(
                self, client, "faucet.devnet.rippletest.net"
            )

    def _parallel_test_generate_faucet_wallet_custom_host_sync_json_rpc(self):
        client = JsonRpcClient("https://s.devnet.rippletest.net:51234")
        sync_generate_faucet_wallet_and_fund_again(
            self, client, "faucet.devnet.rippletest.net"
        )

    # Network tests

    async def _parallel_test_generate_faucet_wallet_testnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://s.altnet.rippletest.net:51233"
        ) as client:
            await generate_faucet_wallet_and_fund_again(self, client)

    async def _parallel_test_generate_faucet_wallet_devnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://s.devnet.rippletest.net:51233"
        ) as client:
            await generate_faucet_wallet_and_fund_again(self, client)

    async def _parallel_test_generate_faucet_wallet_amm_devnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://amm.devnet.rippletest.net:51233"
        ) as client:
            await generate_faucet_wallet_and_fund_again(self, client)

    async def _parallel_test_generate_faucet_wallet_hooks_v3_testnet_async_websockets(
        self,
    ):
        async with AsyncWebsocketClient(
            "wss://hooks-testnet-v3.xrpl-labs.com"
        ) as client:
            global time_of_last_hooks_faucet_call
            # Wait at least 10 seconds since last call to hooks v3 testnet faucet
            time_since_last_hooks_call = time.time() - time_of_last_hooks_faucet_call
            if time_since_last_hooks_call < 10:
                time.sleep(11 - time_since_last_hooks_call)

            wallet = await generate_faucet_wallet(
                client, usage_context="integration_test"
            )
            time_of_last_hooks_faucet_call = time.time()

            result = await client.request(
                AccountInfo(
                    account=wallet.address,
                ),
            )
            balance = int(result.result["account_data"]["Balance"])
            self.assertTrue(balance > 0)

    # Named different from test_generate_faucet_wallet_hooks_v3_testnet_async_websockets
    # so the test runs far from each other since hooks v3 testnet faucet
    # requires 10 seconds between calls
    async def test_fund_given_wallet_hooks_v3_testnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://hooks-testnet-v3.xrpl-labs.com"
        ) as client:
            global time_of_last_hooks_faucet_call
            wallet = Wallet.create()
            time_since_last_hooks_call = time.time() - time_of_last_hooks_faucet_call
            if time_since_last_hooks_call < 10:
                time.sleep(11 - time_since_last_hooks_call)
            time_of_last_hooks_faucet_call = time.time()
            await generate_faucet_wallet(client, wallet)
            result = await client.request(
                AccountInfo(
                    account=wallet.address,
                ),
            )
            balance = int(result.result["account_data"]["Balance"])

            # Wait at least 10 seconds since last call to hooks v3 testnet faucet
            time_since_last_hooks_call = time.time() - time_of_last_hooks_faucet_call
            if time_since_last_hooks_call < 10:
                time.sleep(11 - time_since_last_hooks_call)
            time_of_last_hooks_faucet_call = time.time()

            new_wallet = await generate_faucet_wallet(
                client, wallet, usage_context="integration_test"
            )
            new_result = await client.request(
                AccountInfo(
                    account=new_wallet.address,
                ),
            )
            new_balance = int(new_result.result["account_data"]["Balance"])
            self.assertTrue(new_balance > balance)

    def test_wallet_get_xaddress(self):
        wallet = Wallet.create()
        expected = classic_address_to_xaddress(wallet.address, None, False)
        self.assertEqual(wallet.get_xaddress(), expected)
