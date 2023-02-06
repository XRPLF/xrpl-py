import asyncio

from tests.integration.it_utils import fund_wallet, sign_and_reliable_submission_async
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import (
    OfferCreate,
    Payment,
    PaymentChannelCreate,
    TrustSet
)
from xrpl.wallet import Wallet


# TODO: use `asyncio.gather` for these, to parallelize
# TODO: set up wallet for each test instead of using one for all tests (now that it's
# faster)
async def _set_up_reusable_values():
    WALLET = Wallet.create()
    await fund_wallet(WALLET)
    DESTINATION = Wallet.create()
    await fund_wallet(DESTINATION)
    GATEWAY = Wallet.create()
    await fund_wallet(GATEWAY)

    await sign_and_reliable_submission_async(
        TrustSet(
            account=WALLET.classic_address,
            sequence=WALLET.sequence,
            limit_amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=GATEWAY.classic_address,
                value="10000",
            ),
        ),
        WALLET,
    )
    WALLET.sequence += 1

    await sign_and_reliable_submission_async(
        TrustSet(
            account=DESTINATION.classic_address,
            sequence=DESTINATION.sequence,
            limit_amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=GATEWAY.classic_address,
                value="10000",
            ),
        ),
        DESTINATION,
    )
    DESTINATION.sequence += 1

    await sign_and_reliable_submission_async(
        Payment(
            account=GATEWAY.classic_address,
            sequence=GATEWAY.sequence,
            destination=WALLET.classic_address,
            amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=GATEWAY.classic_address,
                value="10000",
            ),
        ),
        GATEWAY,
    )
    GATEWAY.sequence += 1

    await sign_and_reliable_submission_async(
        Payment(
            account=GATEWAY.classic_address,
            sequence=GATEWAY.sequence,
            destination=DESTINATION.classic_address,
            amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=GATEWAY.classic_address,
                value="10000",
            ),
        ),
        GATEWAY,
    )
    GATEWAY.sequence += 1

    OFFER = await sign_and_reliable_submission_async(
        OfferCreate(
            account=WALLET.classic_address,
            sequence=WALLET.sequence,
            taker_gets="13100000",
            taker_pays=IssuedCurrencyAmount(
                currency="USD",
                issuer=WALLET.classic_address,
                value="10",
            ),
        ),
        WALLET,
    )
    WALLET.sequence += 1

    PAYMENT_CHANNEL = await sign_and_reliable_submission_async(
        PaymentChannelCreate(
            account=WALLET.classic_address,
            sequence=WALLET.sequence,
            amount="1",
            destination=DESTINATION.classic_address,
            settle_delay=86400,
            public_key=WALLET.public_key,
        ),
        WALLET,
    )
    WALLET.sequence += 1

    return (
        WALLET,
        DESTINATION,
        GATEWAY,
        OFFER,
        PAYMENT_CHANNEL,
    )


(
    WALLET,
    DESTINATION,
    GATEWAY,
    OFFER,
    PAYMENT_CHANNEL,
) = asyncio.run(_set_up_reusable_values())
