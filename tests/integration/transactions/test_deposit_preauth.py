from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction, submit_transaction_async
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DepositPreauth

ACCOUNT = WALLET.classic_address
ADDRESS = "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de"


class TestDepositPreauth(IsolatedAsyncioTestCase):
    def test_authorize_sync(self):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            authorize=ADDRESS,
        )
        response = submit_transaction(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1

    def test_unauthorize_sync(self):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            unauthorize=ADDRESS,
        )
        response = submit_transaction(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1

    async def test_authorize_async(self):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            authorize=ADDRESS,
        )
        response = await submit_transaction_async(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1

    async def test_unauthorize_async(self):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            unauthorize=ADDRESS,
        )
        response = await submit_transaction_async(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1
