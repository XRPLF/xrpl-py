from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_mpt_token_and_authorize_source_async,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.requests.ledger_entry import LedgerEntry, Offer
from xrpl.models.transactions import (
    MPTokenIssuanceCreateFlag,
    OfferCreate,
    TrustSet,
    TrustSetFlag,
)
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
    async def test_offer_create_with_MPT(self, client):
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

        taker_gets = MPTAmount(mpt_issuance_id=mpt_issuance_id, value="10")
        response = await sign_and_reliable_submission_async(
            OfferCreate(
                account=source.classic_address,
                taker_gets=taker_gets,
                taker_pays="100000",
            ),
            source,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        offer_seq = response.result["tx_json"]["Sequence"]

        # Validate the offer using ledger_entry
        ledger_entry_response = await client.request(
            LedgerEntry(offer=Offer(account=source.classic_address, seq=offer_seq))
        )
        offer_node = ledger_entry_response.result["node"]
        self.assertEqual(offer_node["LedgerEntryType"], "Offer")
        self.assertEqual(offer_node["Account"], source.classic_address)
        self.assertEqual(
            offer_node["TakerGets"],
            {"mpt_issuance_id": mpt_issuance_id, "value": "10"},
        )
        self.assertEqual(offer_node["TakerPays"], "100000")

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
