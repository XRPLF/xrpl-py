"""A snippet that walks us through an example usage of RegularKey."""
from xrpl.asyncio.account import get_balance
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.models.transactions import Payment, SetRegularKey


async def async_set_regular_key() -> None:
    """
    Async snippet that walks us through an example usage of RegularKey.

    Args:
        client: The async network client to use to send the request.
    """
    async with AsyncWebsocketClient("wss://s.altnet.rippletest.net:51233") as client:
        await client.open()

        # creating wallets as prerequisite
        wallet1 = await generate_faucet_wallet(client, debug=True)
        wallet2 = await generate_faucet_wallet(client, debug=True)
        regular_key_wallet = await generate_faucet_wallet(client, debug=True)

        print("Balances before payment:")
        print(await get_balance(wallet1.classic_address, client))
        print(await get_balance(wallet2.classic_address, client))

        # assigns key-pair(regularKeyWallet) to wallet1 using `SetRegularKey`
        tx = SetRegularKey(
            account=wallet1.classic_address, regular_key=regular_key_wallet.classic_address
        )

        signed_tx = await safe_sign_and_autofill_transaction(tx, wallet1, client)
        set_regular_key_response = await send_reliable_submission(signed_tx, client)

        print("Response for successful SetRegularKey tx")
        print(set_regular_key_response)

        # when wallet1 sends payment to wallet2 andd
        # signs using the regular key wallet, the transaction goes through.
        payment = Payment(
            account=wallet1.classic_address,
            destination=wallet2.classic_address,
            amount="5551000",
        )

        signed_payment = await safe_sign_and_autofill_transaction(
            payment, regular_key_wallet, client
        )
        payment_response = await send_reliable_submission(signed_payment, client)

        print("Response for tx signed using Regular Key:")
        print(payment_response)

        print("Balances after payment:")
        print(await get_balance(wallet1.classic_address, client))
        print(await get_balance(wallet2.classic_address, client))

        await client.close()


# uncomment the lines below to run the snippet
# import asyncio
# asyncio.run(async_set_regular_key())
