from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models import (
    AccountSet,
    AccountSetAsfFlag,
    Clawback,
    IssuedCurrencyAmount,
    Payment,
    TrustSet,
    TrustSetFlag,
)
from xrpl.wallet import Wallet


class TestClawback(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        # test setup
        HOLDER = Wallet.create()
        await fund_wallet(HOLDER)

        await sign_and_reliable_submission_async(
            AccountSet(
                account=WALLET.classic_address,
                set_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
            ),
            WALLET,
        )

        await sign_and_reliable_submission_async(
            TrustSet(
                account=HOLDER.classic_address,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=WALLET.classic_address,
                    currency="USD",
                    value="1000",
                ),
            ),
            HOLDER,
        )

        await sign_and_reliable_submission_async(
            Payment(
                account=WALLET.classic_address,
                destination=HOLDER.classic_address,
                amount=IssuedCurrencyAmount(
                    currency="USD", issuer=WALLET.classic_address, value="1000"
                ),
            ),
            WALLET,
        )

        # actual test - clawback
        response = await sign_and_reliable_submission_async(
            Clawback(
                account=WALLET.classic_address,
                amount=IssuedCurrencyAmount(
                    issuer=HOLDER.classic_address,
                    currency="USD",
                    value="100",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
