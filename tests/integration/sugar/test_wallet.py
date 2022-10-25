from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.clients import AsyncJsonRpcClient, AsyncWebsocketClient
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.asyncio.wallet.wallet_generation import XRPLFaucetException
from xrpl.clients import JsonRpcClient, WebsocketClient
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.models.requests import AccountInfo
from xrpl.models.transactions import Payment
from xrpl.wallet import generate_faucet_wallet as sync_generate_faucet_wallet


class TestWallet(IntegrationTestCase):
    @test_async_and_sync(
        globals(),
        ["xrpl.wallet.generate_faucet_wallet"],
        num_retries=5,
        use_testnet=True,
    )
    async def test_generate_faucet_wallet_rel_sub(self, client):
        destination = await generate_faucet_wallet(client)
        wallet = await generate_faucet_wallet(client)
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

    async def test_generate_faucet_wallet_custom_host_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://xls20-sandbox.rippletest.net:51233"
        ) as client:
            wallet = await generate_faucet_wallet(
                client, faucet_host="faucet-nft.ripple.com"
            )
            result = await client.request(
                AccountInfo(
                    account=wallet.classic_address,
                ),
            )
            self.assertTrue(int(result.result["account_data"]["Balance"]) > 0)

    async def test_generate_faucet_wallet_custom_host_async_json_rpc(self):
        client = AsyncJsonRpcClient("http://xls20-sandbox.rippletest.net:51234")
        wallet = await generate_faucet_wallet(
            client, faucet_host="faucet-nft.ripple.com"
        )
        result = await client.request(
            AccountInfo(
                account=wallet.classic_address,
            ),
        )
        self.assertTrue(int(result.result["account_data"]["Balance"]) > 0)

    def test_generate_faucet_wallet_custom_host_sync_websockets(self):
        with WebsocketClient("wss://xls20-sandbox.rippletest.net:51233") as client:
            wallet = sync_generate_faucet_wallet(
                client, faucet_host="faucet-nft.ripple.com"
            )
            result = client.request(
                AccountInfo(
                    account=wallet.classic_address,
                ),
            )
            self.assertTrue(int(result.result["account_data"]["Balance"]) > 0)

    def test_generate_faucet_wallet_custom_host_sync_json_rpc(self):
        client = JsonRpcClient("http://xls20-sandbox.rippletest.net:51234")
        wallet = sync_generate_faucet_wallet(
            client, faucet_host="faucet-nft.ripple.com"
        )
        result = client.request(
            AccountInfo(
                account=wallet.classic_address,
            ),
        )
        self.assertTrue(int(result.result["account_data"]["Balance"]) > 0)

    async def test_generate_faucet_wallet_testnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://s.altnet.rippletest.net:51233"
        ) as client:
            wallet = await generate_faucet_wallet(client)
            result = await client.request(
                AccountInfo(
                    account=wallet.classic_address,
                ),
            )
            balance = int(result.result["account_data"]["Balance"])
            self.assertTrue(balance > 0)

            new_wallet = await generate_faucet_wallet(client, wallet)
            new_result = await client.request(
                AccountInfo(
                    account=new_wallet.classic_address,
                ),
            )
            new_balance = int(new_result.result["account_data"]["Balance"])
            self.assertTrue(new_balance > balance)

    async def test_generate_faucet_wallet_devnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://s.devnet.rippletest.net:51233"
        ) as client:
            wallet = await generate_faucet_wallet(client)
            result = await client.request(
                AccountInfo(
                    account=wallet.classic_address,
                ),
            )
            balance = int(result.result["account_data"]["Balance"])
            self.assertTrue(balance > 0)

            new_wallet = await generate_faucet_wallet(client, wallet)
            new_result = await client.request(
                AccountInfo(
                    account=new_wallet.classic_address,
                ),
            )
            new_balance = int(new_result.result["account_data"]["Balance"])
            self.assertTrue(new_balance > balance)

    async def test_generate_faucet_wallet_nft_devnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "ws://xls20-sandbox.rippletest.net:51233"
        ) as client:
            wallet = await generate_faucet_wallet(client)
            result = await client.request(
                AccountInfo(
                    account=wallet.classic_address,
                ),
            )
            balance = int(result.result["account_data"]["Balance"])
            self.assertTrue(balance > 0)

            new_wallet = await generate_faucet_wallet(client, wallet)
            new_result = await client.request(
                AccountInfo(
                    account=new_wallet.classic_address,
                ),
            )
            new_balance = int(new_result.result["account_data"]["Balance"])
            self.assertTrue(new_balance > balance)

    async def test_generate_faucet_wallet_amm_devnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://amm.devnet.rippletest.net:51233"
        ) as client:
            wallet = await generate_faucet_wallet(client)
            result = await client.request(
                AccountInfo(
                    account=wallet.classic_address,
                ),
            )
            balance = int(result.result["account_data"]["Balance"])
            self.assertTrue(balance > 0)

            new_wallet = await generate_faucet_wallet(client, wallet)
            new_result = await client.request(
                AccountInfo(
                    account=new_wallet.classic_address,
                ),
            )
            new_balance = int(new_result.result["account_data"]["Balance"])
            self.assertTrue(new_balance > balance)

    async def test_generate_faucet_wallet_hooks_v2_testnet_async_websockets(self):
        async with AsyncWebsocketClient(
            "wss://hooks-testnet-v2.xrpl-labs.com"
        ) as client:
            wallet = await generate_faucet_wallet(client)
            result = await client.request(
                AccountInfo(
                    account=wallet.classic_address,
                ),
            )
            balance = int(result.result["account_data"]["Balance"])
            self.assertTrue(balance > 0)

            with self.assertRaises(XRPLFaucetException):
                await generate_faucet_wallet(client, wallet)

    def test_wallet_get_xaddress(self):
        expected = classic_address_to_xaddress(WALLET.classic_address, None, False)
        self.assertEqual(WALLET.get_xaddress(), expected)


# call this function in many async websockets. In json websockets,
# maybe incorporate to be more in depth.
async def test_faucet_wallet_funding(self, wallet, client):
    wallet = await generate_faucet_wallet(client)
    result = await client.request(
        AccountInfo(
            account=wallet.classic_address,
        ),
    )
    balance = int(result.result["account_data"]["Balance"])
    self.assertTrue(balance > 0)

    new_wallet = await generate_faucet_wallet(client, wallet)
    new_result = await client.request(
        AccountInfo(
            account=new_wallet.classic_address,
        ),
    )
    new_balance = int(new_result.result["account_data"]["Balance"])
    self.assertTrue(new_balance > balance)
