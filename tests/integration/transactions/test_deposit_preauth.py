from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DepositPreauth

ACCOUNT = WALLET.classic_address
ADDRESS = "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de"


class TestDepositPreauth(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_authorize(self, client):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=await get_next_valid_seq_number(WALLET.classic_address, client),
            authorize=ADDRESS,
        )
        response = await submit_transaction_async(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_unauthorize(self, client):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=await get_next_valid_seq_number(WALLET.classic_address, client),
            unauthorize=ADDRESS,
        )
        response = await submit_transaction_async(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
