import asyncio
from typing import Any, Dict

from tests.integration.it_utils import (
    ASYNC_JSON_RPC_CLIENT,
    fund_wallet_async,
    sign_and_reliable_submission_async,
)
from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.models import IssuedCurrencyAmount, OfferCreate, PaymentChannelCreate
from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.currencies.xrp import XRP
from xrpl.models.transactions.account_set import AccountSet, AccountSetAsfFlag
from xrpl.models.transactions.amm_create import AMMCreate
from xrpl.models.transactions.payment import Payment
from xrpl.models.transactions.trust_set import TrustSet, TrustSetFlag
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

    AMM = await setup_amm_pool()

    return (
        WALLET,
        DESTINATION,
        OFFER,
        PAYMENT_CHANNEL,
        AMM,
    )


async def setup_amm_pool(
    client: AsyncClient = ASYNC_JSON_RPC_CLIENT,
) -> Dict[str, Any]:
    issuer_wallet = Wallet.create()
    await fund_wallet_async(issuer_wallet)
    lp_wallet = Wallet.create()
    await fund_wallet_async(lp_wallet)
    currency_code = "USD"

    # test prerequisites - create trustline and send funds
    await sign_and_reliable_submission_async(
        AccountSet(
            account=issuer_wallet.classic_address,
            set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE,
        ),
        issuer_wallet,
    )

    await sign_and_reliable_submission_async(
        TrustSet(
            account=lp_wallet.classic_address,
            flags=TrustSetFlag.TF_CLEAR_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer_wallet.classic_address,
                currency=currency_code,
                value="1000",
            ),
        ),
        lp_wallet,
    )

    await sign_and_reliable_submission_async(
        Payment(
            account=issuer_wallet.classic_address,
            destination=lp_wallet.classic_address,
            amount=IssuedCurrencyAmount(
                currency=currency_code,
                issuer=issuer_wallet.classic_address,
                value="500",
            ),
        ),
        issuer_wallet,
    )

    await sign_and_reliable_submission_async(
        AMMCreate(
            account=lp_wallet.classic_address,
            amount="250",
            amount2=IssuedCurrencyAmount(
                issuer=issuer_wallet.classic_address,
                currency=currency_code,
                value="250",
            ),
            trading_fee=12,
        ),
        lp_wallet,
        client,
    )

    return {
        "issuer_wallet": issuer_wallet,
        "lp_wallet": lp_wallet,
        "asset": XRP(),
        "asset2": IssuedCurrency(
            currency=currency_code,
            issuer=issuer_wallet.classic_address,
        ),
    }


(
    WALLET,
    DESTINATION,
    OFFER,
    PAYMENT_CHANNEL,
    AMM,
) = asyncio.run(_set_up_reusable_values())
