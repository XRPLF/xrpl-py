from tests.integration.integration_test_case import DevIntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountSet, Payment


class TestWallet(DevIntegrationTestCase):
    # @retry
    @test_async_and_sync(
        globals(), ["xrpl.wallet.generate_faucet_wallet"], True, num_retries=5
    )
    async def test_generate_faucet_wallet_dev(self, client):
        wallet = await generate_faucet_wallet(client)
        account_set = AccountSet(
            account=wallet.classic_address,
            fee="10",
            sequence=wallet.sequence,
            set_flag=3,
        )
        response = await submit_transaction_async(account_set, wallet, client=client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    # @retry
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

    def test_wallet_get_xaddress(self):
        expected = classic_address_to_xaddress(WALLET.classic_address, None, False)
        self.assertEqual(WALLET.get_xaddress(), expected)
