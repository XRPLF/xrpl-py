from tests.integration.integration_test_case import DevIntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.asyncio.wallet.wallet_generation import _get_faucet_url
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.models.transactions import Payment


class TestWallet(DevIntegrationTestCase):
    @test_async_and_sync(
        globals(), ["xrpl.wallet.generate_faucet_wallet"], num_retries=5
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

    def test_get_faucet_wallet_dev(self):
        json_client_url = "https://s.devnet.rippletest.net:51234"
        ws_client_url = "wss://s.devnet.rippletest.net/"
        expected_faucet = "https://faucet.devnet.rippletest.net/accounts"

        self.assertEqual(_get_faucet_url(json_client_url), expected_faucet)
        self.assertEqual(_get_faucet_url(ws_client_url), expected_faucet)

    def test_wallet_get_xaddress(self):
        expected = classic_address_to_xaddress(WALLET.classic_address, None, False)
        self.assertEqual(WALLET.get_xaddress(), expected)
