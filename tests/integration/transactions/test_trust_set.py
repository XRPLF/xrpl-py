from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import TrustSet, TrustSetFlag
from xrpl.wallet import Wallet


class TestTrustSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        issuer_wallet = Wallet.create()
        response = await sign_and_reliable_submission_async(
            TrustSet(
                account=WALLET.classic_address,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.classic_address,
                    currency="USD",
                    value="100",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
