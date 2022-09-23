"""A snippet that walks us through creating and claiming a Payment Channel."""
from xrpl.asyncio.account import get_balance
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.models.requests import AccountObjects
from xrpl.models.transactions import PaymentChannelClaim, PaymentChannelCreate


async def async_claim_pay_channel(client: AsyncWebsocketClient) -> None:
    """
    Async snippet that walks us through creating and claiming a Payment Channel.

    Args:
        client: The async network client to use to send the request.
    """
    await client.open()

    # creating wallets as prerequisite
    wallet1 = await generate_faucet_wallet(client, debug=True)
    wallet2 = await generate_faucet_wallet(client, debug=True)

    print("Balances of wallets before Payment Channel is claimed:")
    print(await get_balance(wallet1.classic_address, client))
    print(await get_balance(wallet2.classic_address, client))

    # create a Payment Channel, sign, autofill, submit, and wait for tx to be validated
    payment_channel_create = PaymentChannelCreate(
        account=wallet1.classic_address,
        amount="100",
        destination=wallet2.classic_address,
        settle_delay=86400,
        public_key=wallet1.public_key,
    )

    signed_payment_channel_create = await safe_sign_and_autofill_transaction(
        payment_channel_create, wallet1, client
    )
    channel_create_response = await send_reliable_submission(
        signed_payment_channel_create, client
    )
    print(channel_create_response)

    # check that the object was actually created
    account_objects_request = AccountObjects(account=wallet1.classic_address)
    print(await client.request(account_objects_request))

    # destination claims the Payment Channel and we see the balances to verify
    payment_channel_claim = PaymentChannelClaim(
        account=wallet2.classic_address,
        amount="100",
        channel="PLACEHOLDER - need hashPaymentChannel method",
    )

    signed_payment_channel_claim = await safe_sign_and_autofill_transaction(
        payment_channel_claim, wallet1, client
    )
    channel_claim_response = await send_reliable_submission(
        signed_payment_channel_claim, client
    )
    print(channel_claim_response)

    print("Balances of wallets after Payment Channel is claimed:")
    print(get_balance(wallet1.classic_address, client))
    print(get_balance(wallet2.classic_address, client))

    await client.close()


# uncomment the lines below to run the snippet
# import asyncio
# client = AsyncWebsocketClient("wss://s.altnet.rippletest.net:51233")
# asyncio.run(async_claim_pay_channel(client))
