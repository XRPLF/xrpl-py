"""
Integration tests for MPTs on the DEX (XLS-82, MPTokensV2 amendment): offers,
cross-currency payments through MPT order books, checks, and AMMs.
"""

from typing import List

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet,
    fund_wallet_async,
    sign_and_reliable_submission,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.clients.sync_client import SyncClient
from xrpl.models import (
    XRP,
    AccountSet,
    AMMBid,
    AMMClawback,
    AMMCreate,
    AMMDeposit,
    AMMInfo,
    AMMVote,
    AMMWithdraw,
    BookOffers,
    CheckCash,
    CheckCreate,
    IssuedCurrencyAmount,
    LedgerEntry,
    MPTAmount,
    MPTCurrency,
    MPTokenAuthorize,
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
    OfferCreate,
    Payment,
    Response,
    RipplePathFind,
    Subscribe,
    Transaction,
    TrustSet,
    Tx,
    Unsubscribe,
)
from xrpl.models.path import PathStep
from xrpl.models.requests.ledger_entry import AMM, MPToken
from xrpl.models.requests.subscribe import SubscribeBook
from xrpl.models.requests.unsubscribe import UnsubscribeBook
from xrpl.models.transactions.account_set import AccountSetAsfFlag
from xrpl.models.transactions.amm_deposit import AMMDepositFlag
from xrpl.models.transactions.amm_withdraw import AMMWithdrawFlag
from xrpl.utils import get_order_book_changes
from xrpl.wallet import Wallet

# An MPT must allow trading to be used on the DEX, and transfers for holders to
# trade it with each other.
_DEX_FLAGS = (
    MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRADE
    | MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER
)
_HOLDER_BALANCE = "100000"


def _submit(tx: Transaction, wallet: Wallet, client: SyncClient) -> Response:
    response = sign_and_reliable_submission(tx, wallet, client)
    if response.result["engine_result"] != "tesSUCCESS":
        raise AssertionError(f"{tx.transaction_type}: {response.result}")
    return response


async def _submit_async(
    tx: Transaction, wallet: Wallet, client: AsyncClient
) -> Response:
    response = await sign_and_reliable_submission_async(tx, wallet, client)
    if response.result["engine_result"] != "tesSUCCESS":
        raise AssertionError(f"{tx.transaction_type}: {response.result}")
    return response


def _funded_wallets(count: int) -> List[Wallet]:
    wallets = [Wallet.create() for _ in range(count)]
    for wallet in wallets:
        fund_wallet(wallet)
    return wallets


async def _funded_wallets_async(count: int) -> List[Wallet]:
    wallets = [Wallet.create() for _ in range(count)]
    for wallet in wallets:
        await fund_wallet_async(wallet)
    return wallets


def _create_mpt(
    client: SyncClient,
    issuer: Wallet,
    holders: List[Wallet],
    flags: int = _DEX_FLAGS,
) -> str:
    """Create an MPT, then authorize and fund each holder. Returns its ID."""
    response = _submit(
        MPTokenIssuanceCreate(account=issuer.address, flags=flags), issuer, client
    )
    tx = client.request(Tx(transaction=response.result["tx_json"]["hash"]))
    mpt_issuance_id = tx.result["meta"]["mpt_issuance_id"]
    for holder in holders:
        _submit(
            MPTokenAuthorize(
                account=holder.address, mptoken_issuance_id=mpt_issuance_id
            ),
            holder,
            client,
        )
        _submit(
            Payment(
                account=issuer.address,
                destination=holder.address,
                amount=MPTAmount(
                    mpt_issuance_id=mpt_issuance_id, value=_HOLDER_BALANCE
                ),
            ),
            issuer,
            client,
        )
    return mpt_issuance_id


async def _create_mpt_async(
    client: AsyncClient,
    issuer: Wallet,
    holders: List[Wallet],
    flags: int = _DEX_FLAGS,
) -> str:
    """Create an MPT, then authorize and fund each holder. Returns its ID."""
    response = await _submit_async(
        MPTokenIssuanceCreate(account=issuer.address, flags=flags), issuer, client
    )
    tx = await client.request(Tx(transaction=response.result["tx_json"]["hash"]))
    mpt_issuance_id = tx.result["meta"]["mpt_issuance_id"]
    for holder in holders:
        await _submit_async(
            MPTokenAuthorize(
                account=holder.address, mptoken_issuance_id=mpt_issuance_id
            ),
            holder,
            client,
        )
        await _submit_async(
            Payment(
                account=issuer.address,
                destination=holder.address,
                amount=MPTAmount(
                    mpt_issuance_id=mpt_issuance_id, value=_HOLDER_BALANCE
                ),
            ),
            issuer,
            client,
        )
    return mpt_issuance_id


class TestMPTDEX(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_offer_crossing_mpt_xrp(self, client):
        issuer, maker, taker = await _funded_wallets_async(3)
        mpt_id = await _create_mpt_async(client, issuer, [maker])
        await _submit_async(
            MPTokenAuthorize(account=taker.address, mptoken_issuance_id=mpt_id),
            taker,
            client,
        )
        mpt = MPTCurrency(mpt_issuance_id=mpt_id)

        await _submit_async(
            OfferCreate(
                account=maker.address,
                taker_gets=MPTAmount(mpt_issuance_id=mpt_id, value="100"),
                taker_pays="1000000",
            ),
            maker,
            client,
        )
        book = await client.request(BookOffers(taker_gets=mpt, taker_pays=XRP()))
        self.assertEqual(len(book.result["offers"]), 1)
        self.assertEqual(
            book.result["offers"][0]["TakerGets"],
            {"mpt_issuance_id": mpt_id, "value": "100"},
        )

        response = await _submit_async(
            OfferCreate(
                account=taker.address,
                taker_gets="1000000",
                taker_pays=MPTAmount(mpt_issuance_id=mpt_id, value="100"),
            ),
            taker,
            client,
        )
        tx = await client.request(Tx(transaction=response.result["tx_json"]["hash"]))
        changes = get_order_book_changes(tx.result["meta"])
        self.assertEqual(changes[0]["maker_account"], maker.address)
        self.assertEqual(changes[0]["offer_changes"][0]["status"], "filled")
        self.assertEqual(
            changes[0]["offer_changes"][0]["taker_gets"],
            {"mpt_issuance_id": mpt_id, "value": "-100"},
        )

        mptoken = await client.request(
            LedgerEntry(mptoken=MPToken(mpt_issuance_id=mpt_id, account=taker.address))
        )
        self.assertEqual(mptoken.result["node"]["MPTAmount"], "100")
        book = await client.request(BookOffers(taker_gets=mpt, taker_pays=XRP()))
        self.assertEqual(book.result["offers"], [])

    @test_async_and_sync(globals())
    async def test_offer_crossing_mpt_mpt(self, client):
        issuer, maker, taker = await _funded_wallets_async(3)
        mpt_a = await _create_mpt_async(client, issuer, [maker, taker])
        mpt_b = await _create_mpt_async(client, issuer, [maker, taker])

        await _submit_async(
            OfferCreate(
                account=maker.address,
                taker_gets=MPTAmount(mpt_issuance_id=mpt_a, value="200"),
                taker_pays=MPTAmount(mpt_issuance_id=mpt_b, value="100"),
            ),
            maker,
            client,
        )
        book = await client.request(
            BookOffers(
                taker_gets=MPTCurrency(mpt_issuance_id=mpt_a),
                taker_pays=MPTCurrency(mpt_issuance_id=mpt_b),
            )
        )
        self.assertEqual(len(book.result["offers"]), 1)

        # Take half of the offer.
        response = await _submit_async(
            OfferCreate(
                account=taker.address,
                taker_gets=MPTAmount(mpt_issuance_id=mpt_b, value="50"),
                taker_pays=MPTAmount(mpt_issuance_id=mpt_a, value="100"),
            ),
            taker,
            client,
        )
        tx = await client.request(Tx(transaction=response.result["tx_json"]["hash"]))
        offer_change = get_order_book_changes(tx.result["meta"])[0]["offer_changes"][0]
        self.assertEqual(offer_change["status"], "partially-filled")
        self.assertEqual(
            offer_change["taker_gets"], {"mpt_issuance_id": mpt_a, "value": "-100"}
        )
        self.assertEqual(
            offer_change["taker_pays"], {"mpt_issuance_id": mpt_b, "value": "-50"}
        )

    @test_async_and_sync(globals())
    async def test_offer_crossing_iou_mpt(self, client):
        issuer, maker, taker = await _funded_wallets_async(3)
        mpt_id = await _create_mpt_async(client, issuer, [maker])
        await _submit_async(
            MPTokenAuthorize(account=taker.address, mptoken_issuance_id=mpt_id),
            taker,
            client,
        )
        usd = IssuedCurrencyAmount(currency="USD", issuer=issuer.address, value="50")
        await _submit_async(
            AccountSet(
                account=issuer.address, set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE
            ),
            issuer,
            client,
        )
        for wallet in (maker, taker):
            await _submit_async(
                TrustSet(
                    account=wallet.address,
                    limit_amount=usd.to_currency().to_amount("1000"),
                ),
                wallet,
                client,
            )
        await _submit_async(
            Payment(account=issuer.address, destination=taker.address, amount=usd),
            issuer,
            client,
        )

        await _submit_async(
            OfferCreate(
                account=maker.address,
                taker_gets=MPTAmount(mpt_issuance_id=mpt_id, value="100"),
                taker_pays=usd,
            ),
            maker,
            client,
        )
        book = await client.request(
            BookOffers(
                taker_gets=MPTCurrency(mpt_issuance_id=mpt_id),
                taker_pays=usd.to_currency(),
            )
        )
        self.assertEqual(len(book.result["offers"]), 1)

        await _submit_async(
            OfferCreate(
                account=taker.address,
                taker_gets=usd,
                taker_pays=MPTAmount(mpt_issuance_id=mpt_id, value="100"),
            ),
            taker,
            client,
        )
        mptoken = await client.request(
            LedgerEntry(mptoken=MPToken(mpt_issuance_id=mpt_id, account=taker.address))
        )
        self.assertEqual(mptoken.result["node"]["MPTAmount"], "100")

    @test_async_and_sync(globals())
    async def test_payment_through_mpt_order_book(self, client):
        issuer, maker, sender, receiver = await _funded_wallets_async(4)
        mpt_id = await _create_mpt_async(client, issuer, [maker])
        await _submit_async(
            MPTokenAuthorize(account=receiver.address, mptoken_issuance_id=mpt_id),
            receiver,
            client,
        )
        await _submit_async(
            OfferCreate(
                account=maker.address,
                taker_gets=MPTAmount(mpt_issuance_id=mpt_id, value="1000"),
                taker_pays="10000000",
            ),
            maker,
            client,
        )
        deliver = MPTAmount(mpt_issuance_id=mpt_id, value="10")

        # rippled's pathfinder returns the MPT book step with its issuer.
        path_find = await client.request(
            RipplePathFind(
                source_account=sender.address,
                destination_account=receiver.address,
                destination_amount=deliver,
            )
        )
        alternative = path_find.result["alternatives"][0]
        computed_path = alternative["paths_computed"][0]
        self.assertEqual(
            computed_path,
            [{"issuer": issuer.address, "mpt_issuance_id": mpt_id, "type": 96}],
        )

        # Pay with the computed path, then with a hand-built MPT path step.
        # rippled echoes back the steps it decoded from the signed blob.
        for path, expected_path in (
            ([PathStep.from_dict(step) for step in computed_path], computed_path),
            (
                [PathStep(mpt_issuance_id=mpt_id)],
                [{"mpt_issuance_id": mpt_id, "type": 64}],
            ),
        ):
            response = await _submit_async(
                Payment(
                    account=sender.address,
                    destination=receiver.address,
                    amount=deliver,
                    send_max=alternative["source_amount"],
                    paths=[path],
                ),
                sender,
                client,
            )
            tx = await client.request(
                Tx(transaction=response.result["tx_json"]["hash"])
            )
            self.assertEqual(tx.result["tx_json"]["Paths"], [expected_path])

        mptoken = await client.request(
            LedgerEntry(
                mptoken=MPToken(mpt_issuance_id=mpt_id, account=receiver.address)
            )
        )
        self.assertEqual(mptoken.result["node"]["MPTAmount"], "20")

    @test_async_and_sync(globals())
    async def test_check_with_mpt(self, client):
        issuer, sender, receiver = await _funded_wallets_async(3)
        mpt_id = await _create_mpt_async(client, issuer, [sender])

        # The receiver holds no MPToken: cashing the check creates one.
        for cash_field in ("amount", "deliver_min"):
            response = await _submit_async(
                CheckCreate(
                    account=sender.address,
                    destination=receiver.address,
                    send_max=MPTAmount(mpt_issuance_id=mpt_id, value="50"),
                ),
                sender,
                client,
            )
            tx = await client.request(
                Tx(transaction=response.result["tx_json"]["hash"])
            )
            check_id = next(
                node["CreatedNode"]["LedgerIndex"]
                for node in tx.result["meta"]["AffectedNodes"]
                if node.get("CreatedNode", {}).get("LedgerEntryType") == "Check"
            )
            await _submit_async(
                CheckCash(
                    account=receiver.address,
                    check_id=check_id,
                    **{cash_field: MPTAmount(mpt_issuance_id=mpt_id, value="50")},
                ),
                receiver,
                client,
            )

        mptoken = await client.request(
            LedgerEntry(
                mptoken=MPToken(mpt_issuance_id=mpt_id, account=receiver.address)
            )
        )
        self.assertEqual(mptoken.result["node"]["MPTAmount"], "100")

    @test_async_and_sync(globals())
    async def test_amm_with_mpt(self, client):
        issuer, lp, depositor = await _funded_wallets_async(3)
        mpt_id = await _create_mpt_async(
            client,
            issuer,
            [lp, depositor],
            _DEX_FLAGS | MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK,
        )
        mpt = MPTCurrency(mpt_issuance_id=mpt_id)

        await _submit_async(
            AMMCreate(
                account=lp.address,
                amount="10000000",
                amount2=MPTAmount(mpt_issuance_id=mpt_id, value="1000"),
                trading_fee=10,
            ),
            lp,
            client,
        )
        amm_info = await client.request(AMMInfo(asset=XRP(), asset2=mpt))
        self.assertEqual(
            amm_info.result["amm"]["amount2"],
            {"mpt_issuance_id": mpt_id, "value": "1000"},
        )
        amm_entry = await client.request(LedgerEntry(amm=AMM(asset=mpt, asset2=XRP())))
        self.assertEqual(amm_entry.result["node"]["LedgerEntryType"], "AMM")
        self.assertEqual(
            amm_entry.result["node"]["Account"], amm_info.result["amm"]["account"]
        )

        for tx in (
            AMMDeposit(
                account=depositor.address,
                asset=XRP(),
                asset2=mpt,
                amount=MPTAmount(mpt_issuance_id=mpt_id, value="100"),
                flags=AMMDepositFlag.TF_SINGLE_ASSET,
            ),
            AMMVote(account=depositor.address, asset=mpt, asset2=XRP(), trading_fee=20),
            AMMBid(account=depositor.address, asset=mpt, asset2=XRP()),
            AMMWithdraw(
                account=depositor.address,
                asset=XRP(),
                asset2=mpt,
                amount=MPTAmount(mpt_issuance_id=mpt_id, value="50"),
                flags=AMMWithdrawFlag.TF_SINGLE_ASSET,
            ),
        ):
            await _submit_async(tx, depositor, client)

        amm_info = await client.request(AMMInfo(asset=XRP(), asset2=mpt))
        self.assertEqual(amm_info.result["amm"]["amount2"]["value"], "1050")
        self.assertEqual(
            amm_info.result["amm"]["auction_slot"]["account"], depositor.address
        )

        await _submit_async(
            AMMClawback(
                account=issuer.address,
                holder=depositor.address,
                asset=mpt,
                asset2=XRP(),
            ),
            issuer,
            client,
        )
        amm_info = await client.request(AMMInfo(asset=XRP(), asset2=mpt))
        self.assertLess(int(amm_info.result["amm"]["amount2"]["value"]), 1050)

    @test_async_and_sync(globals())
    async def test_amm_with_two_mpts(self, client):
        issuer, lp = await _funded_wallets_async(2)
        mpt_a = await _create_mpt_async(client, issuer, [lp])
        mpt_b = await _create_mpt_async(client, issuer, [lp])
        asset = MPTCurrency(mpt_issuance_id=mpt_a)
        asset2 = MPTCurrency(mpt_issuance_id=mpt_b)

        await _submit_async(
            AMMCreate(
                account=lp.address,
                amount=MPTAmount(mpt_issuance_id=mpt_a, value="1000"),
                amount2=MPTAmount(mpt_issuance_id=mpt_b, value="1000"),
                trading_fee=10,
            ),
            lp,
            client,
        )
        await _submit_async(
            AMMDeposit(
                account=lp.address,
                asset=asset,
                asset2=asset2,
                amount=MPTAmount(mpt_issuance_id=mpt_a, value="100"),
                amount2=MPTAmount(mpt_issuance_id=mpt_b, value="100"),
                flags=AMMDepositFlag.TF_TWO_ASSET,
            ),
            lp,
            client,
        )
        amm_info = await client.request(AMMInfo(asset=asset, asset2=asset2))
        amm = amm_info.result["amm"]
        self.assertEqual(
            {
                amm[key]["mpt_issuance_id"]: amm[key]["value"]
                for key in ("amount", "amount2")
            },
            {mpt_a: "1100", mpt_b: "1100"},
        )

    @test_async_and_sync(globals(), websockets_only=True)
    async def test_book_subscription_with_mpt(self, client):
        issuer, maker = await _funded_wallets_async(2)
        mpt_id = await _create_mpt_async(client, issuer, [maker])
        mpt = MPTCurrency(mpt_issuance_id=mpt_id)
        await _submit_async(
            OfferCreate(
                account=maker.address,
                taker_gets=MPTAmount(mpt_issuance_id=mpt_id, value="100"),
                taker_pays="1000000",
            ),
            maker,
            client,
        )

        response = await client.request(
            Subscribe(
                books=[
                    SubscribeBook(
                        taker_gets=mpt,
                        taker_pays=XRP(),
                        taker=maker.address,
                        snapshot=True,
                    )
                ]
            )
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(
            response.result["offers"][0]["TakerGets"],
            {"mpt_issuance_id": mpt_id, "value": "100"},
        )
        response = await client.request(
            Unsubscribe(books=[UnsubscribeBook(taker_gets=mpt, taker_pays=XRP())])
        )
        self.assertTrue(response.is_successful())
