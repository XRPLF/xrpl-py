"""A snippet that walks us through getting a transaction."""
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.models.requests import Ledger, Tx


async def async_get_transaction(client: AsyncWebsocketClient) -> None:
    """
    Async snippet that walks us through getting a transaction.

    Args:
        client: The async network client to use to send the request.

    Raises:
        Exception: if meta not included in the transaction response.
    """
    await client.open()

    ledger_request = Ledger(transactions=True, ledger_index="validated")
    ledger_response = await client.request(ledger_request)
    print(ledger_response)

    transactions = ledger_response.result["ledger"]["transactions"]

    if transactions:
        tx = await client.request(Tx(transaction=transactions[0]))
        print(tx)

        # the meta field would be a string(hex)
        # when the `binary` parameter is `true` for the `tx` request.
        if tx.result["meta"] is None:
            raise Exception("meta not included in the response")

        # delivered_amount is the amount actually received by the destination account.
        # Use this field to determine how much was delivered,
        # regardless of whether the transaction is a partial payment.
        # https://xrpl.org/transaction-metadata.html#delivered_amount
        if type(tx.result["meta"] != "string"):
            if "delivered_amount" in tx.result["meta"]:
                print("delivered_amount:", tx.result["meta"]["delivered_amount"])
            else:
                print("delivered_amount: undefined")

    await client.close()


# uncomment the lines below to run the snippet
# import asyncio
# client = AsyncWebsocketClient("wss://s.altnet.rippletest.net:51233")
# asyncio.run(async_get_transaction(client))
