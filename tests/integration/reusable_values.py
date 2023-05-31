import asyncio

from tests.integration.it_utils import fund_wallet, sign_and_reliable_submission_async
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import (
    AccountSet,
    AccountSetFlag,
    OfferCreate,
    Payment,
    PaymentChannelCreate,
    TrustSet,
    TrustSetFlag,
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

    OFFER = await sign_and_reliable_submission_async(
        OfferCreate(
            account=WALLET.classic_address,
            taker_gets="13100000",
            taker_pays=IssuedCurrencyAmount(
                currency="USD",
                issuer=WALLET.classic_address,
                value="10",
            ),
        ),
        WALLET,
    )

    PAYMENT_CHANNEL = await sign_and_reliable_submission_async(
        PaymentChannelCreate(
            account=WALLET.classic_address,
            amount="1",
            destination=DESTINATION.classic_address,
            settle_delay=86400,
            public_key=WALLET.public_key,
        ),
        WALLET,
    )

    await sign_and_reliable_submission_async(
        AccountSet(
            account=WALLET.classic_address,
            set_flag=AccountSetFlag.ASF_ALLOW_CLAWBACK,
        ),
        WALLET,
    )

    await sign_and_reliable_submission_async(
        TrustSet(
            account=DESTINATION.classic_address,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=WALLET.classic_address,
                currency="USD",
                value="1000",
            ),
        ),
        DESTINATION,
    )

    await sign_and_reliable_submission_async(
        Payment(
            account=WALLET.classic_address,
            destination=DESTINATION.classic_address,
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=WALLET.classic_address, value="1000"
            ),
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
