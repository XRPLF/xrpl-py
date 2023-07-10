import asyncio

from tests.integration.it_utils import fund_wallet, sign_and_reliable_submission_async
from xrpl.models import (
    AccountSet,
    AccountSetFlag,
    IssuedCurrencyAmount,
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

    CLAWBACK_ISSUER = Wallet.create()
    await fund_wallet(CLAWBACK_ISSUER)
    CLAWBACK_HOLDER = Wallet.create()
    await fund_wallet(CLAWBACK_HOLDER)

    await sign_and_reliable_submission_async(
        AccountSet(
            account=CLAWBACK_ISSUER.classic_address,
            set_flag=AccountSetFlag.ASF_ALLOW_CLAWBACK,
        ),
        CLAWBACK_ISSUER,
    )

    await sign_and_reliable_submission_async(
        TrustSet(
            account=CLAWBACK_HOLDER.classic_address,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=CLAWBACK_ISSUER.classic_address,
                currency="USD",
                value="1000",
            ),
        ),
        CLAWBACK_HOLDER,
    )

    await sign_and_reliable_submission_async(
        Payment(
            account=CLAWBACK_ISSUER.classic_address,
            destination=CLAWBACK_HOLDER.classic_address,
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=CLAWBACK_ISSUER.classic_address, value="1000"
            ),
        ),
        CLAWBACK_ISSUER,
    )

    return (
        WALLET,
        DESTINATION,
        OFFER,
        PAYMENT_CHANNEL,
        CLAWBACK_ISSUER,
        CLAWBACK_HOLDER,
    )


(
    WALLET,
    DESTINATION,
    OFFER,
    PAYMENT_CHANNEL,
    CLAWBACK_ISSUER,
    CLAWBACK_HOLDER,
) = asyncio.run(_set_up_reusable_values())
