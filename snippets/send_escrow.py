"""A snippet that walks us through creating and finishing escrows."""
from datetime import datetime

from xrpl.asyncio.account import get_balance
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.models.requests import AccountObjects
from xrpl.models.transactions import EscrowCreate, EscrowFinish
from xrpl.utils import datetime_to_ripple_time


async def async_send_escrow() -> None:
    """
    Async snippet that walks us through creating and finishing escrows.

    Args:
        client: The async network client to use to send the request.
    """
    async with AsyncWebsocketClient("wss://s.altnet.rippletest.net:51233") as client:
        await client.open()

        # creating wallets as prerequisite
        wallet1 = await generate_faucet_wallet(client, debug=True)
        wallet2 = await generate_faucet_wallet(client, debug=True)

        print("Balances of wallets before Escrow tx was created:")
        print(await get_balance(wallet1.classic_address, client))
        print(await get_balance(wallet2.classic_address, client))

        finish_after = datetime_to_ripple_time(datetime.now()) + 2

        create_tx = EscrowCreate(
            account=wallet1.classic_address,
            destination=wallet2.classic_address,
            amount="1000000",
            finish_after=finish_after,
        )

        signed_create_tx = await safe_sign_and_autofill_transaction(
            create_tx, wallet1, client
        )
        create_escrow_response = await send_reliable_submission(signed_create_tx, client)

        print(create_escrow_response)

        # check that the object was actually created
        account_objects_request = AccountObjects(account=wallet1.classic_address)
        account_objects = (await client.request(account_objects_request)).result[
            "account_objects"
        ]

        print("Escrow object exists in wallet1's account")
        print(account_objects)

        finish_tx = EscrowFinish(
            account=wallet1.classic_address,
            owner=wallet1.classic_address,
            offer_sequence=create_escrow_response.result["Sequence"],
        )

        signed_finish_tx = await safe_sign_and_autofill_transaction(
            finish_tx, wallet1, client
        )
        await send_reliable_submission(signed_finish_tx, client)

        print("Balances of wallets after Escrow was sent")
        print(await get_balance(wallet1.classic_address, client))
        print(await get_balance(wallet2.classic_address, client))

        await client.close()


# uncomment the lines below to run the snippet
# import asyncio
# asyncio.run(async_send_escrow())
