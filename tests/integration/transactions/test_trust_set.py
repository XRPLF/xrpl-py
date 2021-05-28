try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import TrustSet, TrustSetFlag
from xrpl.wallet import Wallet


class TestTrustSet(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        issuer_wallet = Wallet.create()
        response = await submit_transaction_async(
            TrustSet(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.classic_address,
                    currency="USD",
                    value="100",
                ),
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
