import asyncio

from tests.integration.it_utils import (
    MASTER_ACCOUNT,
    fund_wallet_async,
    sign_and_reliable_submission_async,
)
from xrpl.models import (
    XRP,
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

    return (
        wallet,
        destination,
        door_wallet,
        witness_wallet,
        offer,
        payment_channel,
        bridge,
    )


(
    WALLET,
    DESTINATION,
    DOOR_WALLET,
    WITNESS_WALLET,
    OFFER,
    PAYMENT_CHANNEL,
    BRIDGE,
) = asyncio.run(_set_up_reusable_values())
