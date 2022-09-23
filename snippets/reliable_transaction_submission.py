"""A snippet that walks us through sending a transaction reliably."""
from xrpl.asyncio.account import get_balance
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.models.requests import Tx
from xrpl.models.transactions import Payment

#  When implementing Reliable Transaction Submission, there are many potential
#  solutions, each with different trade-offs.
#  The main decision points are:
#  1) Transaction preparation:
#     - The autofill function as a part of the submitAndWait should be able to
#       correctly populate values for the fields Sequence, LastLedgerSequence and Fee.
#  2) Transaction status retrieval. Options include:
#     - Poll for transaction status:
#       - On a regular interval (e.g. Every 3-5 seconds), or
#       - When a new validated ledger is detected
#       + (To accommodate an edge case in transaction retrieval,
#          check the sending account's Sequence number to confirm that it has the
#          expected value; alternatively, wait until a few additional ledgers have
#          been validated before deciding that atransaction has definitively not
#          been included in a validated ledger)
#     - Listen for transaction status: scan all validated transactions to see if our
#       transactions are among them
#  3) What do we do when a transaction fails? It is possible to implement retry logic,
#     but caution is advised.
#  Note that there are a few ways for a transaction to fail:
#     A) `tec`: The transaction was included in a ledger but only claimed the
#               transaction fee
#     B) `tesSUCCESS` but unexpected result: The transaction was successful but did not
#                                            have the expected result. This generally
#                                            does not occur for XRP-to-XRP payments
#     C) The transaction was not, and never will be, included in a validated
#        ledger [3C].

#  References:
#  - https://xrpl.org/reliable-transaction-submission.html
#  - https://xrpl.org/send-xrp.html
#  - https://xrpl.org/look-up-transaction-results.html
#  - https://xrpl.org/monitor-incoming-payments-with-websocket.html.

#  For the implementation in this example, we have made the following decisions:
#  1) We allow the autofill function as a part of submitAndWait to fill up the account
#     sequence, LastLedgerSequence and Fee. Payments are defined upfront, and
#     idempotency is not needed. If the script is run a second time, duplicate
#     payments will result.
#  2) We will rely on the xrpl.js submitAndWait function to get us the transaction
#     submission result after the wait time.
#  3) Transactions will not be automatically retried. Transactions are limited to
#     XRP-to-XRP payments and cannot "succeed" in an unexpected way.


async def async_send_reliable_tx(client: AsyncWebsocketClient) -> None:
    """
    Async snippet that walks us through sending a transaction reliably.

    Args:
        client: The async network client to use to send the request.
    """
    await client.open()

    # creating wallets as prerequisite
    wallet1 = await generate_faucet_wallet(client, debug=True)
    wallet2 = await generate_faucet_wallet(client, debug=True)

    print("Balances of wallets before Payment tx")
    print(await get_balance(wallet1.classic_address, client))
    print(await get_balance(wallet2.classic_address, client))

    # create a Payment tx and submit and wait for tx to be validated
    payment_tx = Payment(
        account=wallet1.classic_address,
        amount="1000",
        destination=wallet2.classic_address,
    )

    signed_payment_tx = await safe_sign_and_autofill_transaction(
        payment_tx, wallet1, client
    )
    payment_response = await send_reliable_submission(signed_payment_tx, client)
    print("\nTransaction was submitted.\n")
    tx_response = await client.request(Tx(transaction=payment_response.result["hash"]))
    # with the following reponse we are able to see that the tx was indeed validated
    print("Validated:", tx_response.result["validated"])

    print("Balances of wallets after Payment tx:")
    print(await get_balance(wallet1.classic_address, client))
    print(await get_balance(wallet2.classic_address, client))

    await client.close()


# uncomment the lines below to run the snippet
# import asyncio
# client = AsyncWebsocketClient("wss://s.altnet.rippletest.net:51233")
# asyncio.run(async_send_reliable_tx(client))
