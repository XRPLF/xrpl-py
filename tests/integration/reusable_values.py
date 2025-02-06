import asyncio
from typing import Any, Dict

from tests.integration.it_utils import (
    ASYNC_JSON_RPC_CLIENT,
    MASTER_ACCOUNT,
    create_amm_pool_async,
    fund_wallet_async,
    sign_and_reliable_submission_async,
)
from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.models import (
    XRP,
    AMMDeposit,
    AMMDepositFlag,
    IssuedCurrencyAmount,
    OfferCreate,
    PaymentChannelCreate,
    SignerEntry,
    SignerListSet,
    XChainBridge,
    XChainCreateBridge,
)
from xrpl.wallet import Wallet


# TODO: use `asyncio.gather` for these, to parallelize
# TODO: set up wallet for each test instead of using one for all tests (now that it's
# faster)
async def _set_up_reusable_values():
    wallet = Wallet.create()
    await fund_wallet_async(wallet)
    destination = Wallet.create()
    await fund_wallet_async(destination)
    door_wallet = Wallet.create()
    await fund_wallet_async(door_wallet)
    witness_wallet = Wallet.create()
    await fund_wallet_async(witness_wallet)

    offer = await sign_and_reliable_submission_async(
        OfferCreate(
            account=wallet.address,
            taker_gets="13100000",
            taker_pays=IssuedCurrencyAmount(
                currency="USD",
                issuer=wallet.address,
                value="10",
            ),
        ),
        wallet,
    )

    payment_channel = await sign_and_reliable_submission_async(
        PaymentChannelCreate(
            account=wallet.address,
            amount="1",
            destination=destination.address,
            settle_delay=86400,
            public_key=wallet.public_key,
        ),
        wallet,
    )

    bridge = XChainCreateBridge(
        account=door_wallet.address,
        xchain_bridge=XChainBridge(
            locking_chain_door=door_wallet.address,
            locking_chain_issue=XRP(),
            issuing_chain_door=MASTER_ACCOUNT,
            issuing_chain_issue=XRP(),
        ),
        signature_reward="200",
        min_account_create_amount="10000000",
    )
    await sign_and_reliable_submission_async(
        bridge,
        door_wallet,
    )
    await sign_and_reliable_submission_async(
        SignerListSet(
            account=door_wallet.classic_address,
            signer_entries=[
                SignerEntry(
                    account=witness_wallet.classic_address,
                    signer_weight=1,
                )
            ],
            signer_quorum=1,
        ),
        door_wallet,
    )

    setup_amm_pool_res = await setup_amm_pool(wallet=wallet)
    amm_asset = setup_amm_pool_res["asset"]
    amm_asset2 = setup_amm_pool_res["asset2"]
    amm_issuer_wallet = setup_amm_pool_res["issuer_wallet"]

    return (
        wallet,
        destination,
        door_wallet,
        witness_wallet,
        offer,
        payment_channel,
        amm_asset,
        amm_asset2,
        amm_issuer_wallet,
        bridge,
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
    DOOR_WALLET,
    WITNESS_WALLET,
    OFFER,
    PAYMENT_CHANNEL,
    AMM_ASSET,
    AMM_ASSET2,
    AMM_ISSUER_WALLET,
    BRIDGE,
) = asyncio.run(_set_up_reusable_values())
