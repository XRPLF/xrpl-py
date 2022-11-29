from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import TrustSet, TrustSetFlag
from xrpl.wallet import Wallet


class TestTrustSet(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_basic_functionality(self, client):
        issuer_wallet = Wallet.create()
        response = await submit_transaction_async(
            TrustSet(
                account=WALLET.classic_address,
                sequence=await get_next_valid_seq_number(
                    WALLET.classic_address, client
                ),
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
