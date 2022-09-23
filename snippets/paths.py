"""A snippet that walks us through creating a transaction with a path."""
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.transaction import safe_sign_and_autofill_transaction
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.currencies.xrp import XRP
from xrpl.models.requests import RipplePathFind
from xrpl.models.transactions import Payment


async def async_create_tx_with_paths(client: AsyncWebsocketClient) -> None:
    """
    Async snippet that walks us through creating a transaction with a path.

    Args:
        client: The async network client to use to send the request.
    """
    await client.open()

    wallet = await generate_faucet_wallet(client, debug=True)
    destination_account = "rKT4JX4cCof6LcDYRz8o3rGRu7qxzZ2Zwj"
    destination_amount = IssuedCurrencyAmount(
        value="0.001",
        currency="USD",
        issuer="rVnYNK9yuxBz4uP8zC8LEFokM2nqH3poc",
    )

    path_request = RipplePathFind(
        source_account=wallet.classic_address,
        source_currencies=[XRP()],
        destination_account=destination_account,
        destination_amount=destination_amount,
    )

    path_response = await client.request(path_request)
    print(path_response)

    paths = path_response.result["alternatives"][0]["paths_computed"]
    print(paths)

    payment_tx = Payment(
        account=wallet.classic_address,
        amount=destination_amount,
        destination=destination_account,
        paths=paths,
    )

    print(
        "signed: ", await safe_sign_and_autofill_transaction(payment_tx, wallet, client)
    )

    await client.close()


# uncomment the lines below to run the snippet
# import asyncio
# client = AsyncWebsocketClient("wss://s.altnet.rippletest.net:51233")
# asyncio.run(async_create_tx_with_paths(client))
