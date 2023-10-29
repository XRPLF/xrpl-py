import asyncio
from typing import Any, Dict

from tests.integration.it_utils import (
    ASYNC_JSON_RPC_CLIENT,
    create_amm_pool_async,
    fund_wallet_async,
    sign_and_reliable_submission_async,
)
from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.models import IssuedCurrencyAmount, OfferCreate, PaymentChannelCreate
from xrpl.models.transactions.amm_deposit import AMMDeposit, AMMDepositFlag
from xrpl.wallet import Wallet


# TODO: use `asyncio.gather` for these, to parallelize
# TODO: set up wallet for each test instead of using one for all tests (now that it's
# faster)
async def _set_up_reusable_values():
    WALLET = Wallet.create()
    await fund_wallet_async(WALLET)
    DESTINATION = Wallet.create()
    await fund_wallet_async(DESTINATION)

    OFFER = await sign_and_reliable_submission_async(
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
    )

    PAYMENT_CHANNEL = await sign_and_reliable_submission_async(
        PaymentChannelCreate(
            account=WALLET.address,
            amount="1",
            destination=DESTINATION.address,
            settle_delay=86400,
            public_key=WALLET.public_key,
        ),
        WALLET,
    )

    setup_amm_pool_res = await setup_amm_pool(wallet=WALLET)
    AMM_ASSET = setup_amm_pool_res["asset"]
    AMM_ASSET2 = setup_amm_pool_res["asset2"]
    AMM_ISSUER_WALLET = setup_amm_pool_res["issuer_wallet"]

    return (
        WALLET,
        DESTINATION,
        OFFER,
        PAYMENT_CHANNEL,
        AMM_ASSET,
        AMM_ASSET2,
        AMM_ISSUER_WALLET,
    )


async def setup_amm_pool(
    wallet: Wallet,
    client: AsyncClient = ASYNC_JSON_RPC_CLIENT,
) -> Dict[str, Any]:
    amm_pool = await create_amm_pool_async(client=client)
    asset = amm_pool["asset"]
    asset2 = amm_pool["asset2"]
    issuer_wallet = amm_pool["issuer_wallet"]

    # Need to deposit (be an LP) to make bid/vote/withdraw eligible in tests for WALLET
    await sign_and_reliable_submission_async(
        AMMDeposit(
            account=wallet.classic_address,
            asset=asset,
            asset2=asset2,
            amount="1000",
            flags=AMMDepositFlag.TF_SINGLE_ASSET,
        ),
        wallet,
        client,
    )

    return {
        "asset": asset,
        "asset2": asset2,
        "issuer_wallet": issuer_wallet,
    }


(
    WALLET,
    DESTINATION,
    OFFER,
    PAYMENT_CHANNEL,
    AMM_ASSET,
    AMM_ASSET2,
    AMM_ISSUER_WALLET,
) = asyncio.run(_set_up_reusable_values())
