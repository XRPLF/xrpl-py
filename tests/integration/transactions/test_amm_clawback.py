from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_amm_pool_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.currencies.xrp import XRP
from xrpl.models.transactions import AMMDeposit
from xrpl.models.transactions.amm_clawback import AMMClawback
from xrpl.models.transactions.amm_deposit import AMMDepositFlag


class TestAMMClawback(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_positive_workflow(self, client):
        amm_pool = await create_amm_pool_async(client, enable_amm_clawback=True)

        # Asset-1 is XRP, Asset-2 is an IssuedCurrency titled "USD"
        # The Issuer of Asset-2 is the issuer_wallet
        # For the purposes of this test, the issuer_wallet has set the
        # Allow Trust Line Clawback flag
        issuer_wallet = amm_pool["issuer_wallet"]
        holder_wallet = amm_pool["lp_wallet"]

        # "holder" account deposits both assets into the AMM pool
        # Deposit assets into AMM pool
        amm_deposit = AMMDeposit(
            account=holder_wallet.address,
            asset=IssuedCurrency(
                currency="USD",
                issuer=issuer_wallet.address,
            ),
            asset2=XRP(),
            amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=issuer_wallet.address,
                value="10",
            ),
            flags=AMMDepositFlag.TF_SINGLE_ASSET,
        )
        deposit_response = await sign_and_reliable_submission_async(
            amm_deposit, holder_wallet, client
        )
        self.assertEqual(deposit_response.result["engine_result"], "tesSUCCESS")

        # Clawback one of the assets from the AMM pool
        amm_clawback = AMMClawback(
            account=issuer_wallet.address,
            holder=holder_wallet.address,
            asset=IssuedCurrency(
                currency="USD",
                issuer=issuer_wallet.address,
            ),
            asset2=XRP(),
        )
        clawback_response = await sign_and_reliable_submission_async(
            amm_clawback, issuer_wallet, client
        )
        self.assertEqual(clawback_response.result["engine_result"], "tesSUCCESS")
