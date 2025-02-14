from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import OfferCreate, TrustSet, TrustSetFlag
from xrpl.wallet import Wallet


class TestOfferCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        offer = await sign_and_reliable_submission_async(
            OfferCreate(
                account=WALLET.address,
                taker_gets="13100000",
                taker_pays=IssuedCurrencyAmount(
                    currency="USD",
                    issuer=WALLET.address,
                    value="10",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(offer.is_successful())

    @test_async_and_sync(globals())
    async def test_deep_freeze_trustline_fails(self, client):

        issuer_wallet = Wallet.create()
        await fund_wallet_async(issuer_wallet)
        response = await sign_and_reliable_submission_async(
            TrustSet(
                account=WALLET.address,
                flags=TrustSetFlag.TF_SET_FREEZE | TrustSetFlag.TF_SET_DEEP_FREEZE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.address,
                    currency="USD",
                    value="100",
                ),
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        offer = await sign_and_reliable_submission_async(
            OfferCreate(
                account=WALLET.address,
                taker_gets="13100000",
                taker_pays=IssuedCurrencyAmount(
                    currency="USD",
                    issuer=issuer_wallet.address,
                    value="10",
                ),
            ),
            WALLET,
            client,
        )

        self.assertEqual(
            offer.result["engine_result"],
            "tecFROZEN",
        )
