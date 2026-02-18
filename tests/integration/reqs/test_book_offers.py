from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_mpt_token_and_authorize_source_async,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import MPTAmount
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.currencies.mpt_currency import MPTCurrency
from xrpl.models.requests import BookOffers
from xrpl.models.transactions import MPTokenIssuanceCreateFlag, OfferCreate
from xrpl.wallet import Wallet


class TestBookOffers(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await client.request(
            BookOffers(
                taker=WALLET.address,
                taker_gets=XRP(),
                taker_pays=IssuedCurrency(
                    currency="USD",
                    issuer="rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                ),
                ledger_index="validated",
            ),
        )
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_book_offers_with_mpt(self, client):
        issuer = Wallet.create()
        await fund_wallet_async(issuer)
        source = Wallet.create()
        await fund_wallet_async(source)

        mpt_issuance_id = await create_mpt_token_and_authorize_source_async(
            issuer=issuer,
            source=source,
            client=client,
            flags=[
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRADE,
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
            ],
        )

        # Create an offer: source sells MPT for XRP
        taker_gets = MPTAmount(mpt_issuance_id=mpt_issuance_id, value="10")
        offer_response = await sign_and_reliable_submission_async(
            OfferCreate(
                account=source.classic_address,
                taker_gets=taker_gets,
                taker_pays="100000",
            ),
            source,
            client,
        )
        self.assertEqual(offer_response.result["engine_result"], "tesSUCCESS")

        # Query book_offers for the MPT/XRP order book
        mpt_currency = MPTCurrency(mpt_issuance_id=mpt_issuance_id)
        response = await client.request(
            BookOffers(
                taker_gets=mpt_currency,
                taker_pays=XRP(),
            )
        )
        self.assertTrue(response.is_successful())

        offers = response.result["offers"]
        self.assertGreaterEqual(len(offers), 1)

        matching = [
            o for o in offers
            if o["Account"] == source.classic_address
        ]
        self.assertEqual(len(matching), 1)
        self.assertEqual(
            matching[0]["TakerGets"],
            {"mpt_issuance_id": mpt_issuance_id, "value": "10"},
        )
        self.assertEqual(matching[0]["TakerPays"], "100000")
