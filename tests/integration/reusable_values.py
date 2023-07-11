import asyncio

from tests.integration.it_utils import fund_wallet, sign_and_reliable_submission_async
from xrpl.models import IssuedCurrencyAmount, OfferCreate, PaymentChannelCreate
from xrpl.wallet import Wallet


# TODO: use `asyncio.gather` for these, to parallelize
# TODO: set up wallet for each test instead of using one for all tests (now that it's
# faster)
async def _set_up_reusable_values():
    WALLET = Wallet.create()
    await fund_wallet(WALLET)
    DESTINATION = Wallet.create()
    await fund_wallet(DESTINATION)

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

    return (
        WALLET,
        DESTINATION,
        OFFER,
        PAYMENT_CHANNEL,
    )


(
    WALLET,
    DESTINATION,
    OFFER,
    PAYMENT_CHANNEL,
) = asyncio.run(_set_up_reusable_values())
