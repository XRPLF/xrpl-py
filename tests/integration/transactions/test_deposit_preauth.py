try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DepositPreauth

ACCOUNT = WALLET.classic_address
ADDRESS = "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de"


class TestDepositPreauth(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_authorize(self, client):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            authorize=ADDRESS,
        )
        response = await submit_transaction_async(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1

    @test_async_and_sync(globals())
    async def test_unauthorize(self, client):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            unauthorize=ADDRESS,
        )
        response = await submit_transaction_async(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1
