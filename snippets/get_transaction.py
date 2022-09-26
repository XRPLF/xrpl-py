"""A snippet that walks us through getting a transaction."""
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import Ledger, Tx


def get_transaction() -> None:
    """
    Sync snippet that walks us through getting a transaction.

    Raises:
        Exception: if meta not included in the transaction response.
    """
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

    ledger_request = Ledger(transactions=True, ledger_index="validated")
    ledger_response = client.request(ledger_request)
    print(ledger_response)

    transactions = ledger_response.result["ledger"]["transactions"]

    if transactions:
        tx_request = Tx(transaction=transactions[0])
        tx_response = client.request(tx_request)
        print(tx_response)

        # the meta field would be a string(hex)
        # when the `binary` parameter is `true` for the `tx` request.
        if tx_response.result["meta"] is None:
            raise Exception("meta not included in the response")

        # delivered_amount is the amount actually received by the destination account.
        # Use this field to determine how much was delivered,
        # regardless of whether the transaction is a partial payment.
        # https://xrpl.org/transaction-metadata.html#delivered_amount
        if type(tx_response.result["meta"] != "string"):
            if "delivered_amount" in tx_response.result["meta"]:
                print(
                    "delivered_amount:", tx_response.result["meta"]["delivered_amount"]
                )
            else:
                print("delivered_amount: undefined")


# uncomment the line below to run the snippet
# get_transaction()
