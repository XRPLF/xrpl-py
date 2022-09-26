"""A snippet that walks us through creating a transaction with a path."""
from xrpl.clients import JsonRpcClient
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.currencies.xrp import XRP
from xrpl.models.requests import RipplePathFind
from xrpl.models.transactions import Payment
from xrpl.transaction import safe_sign_and_autofill_transaction
from xrpl.wallet import generate_faucet_wallet


def create_tx_with_paths(client: JsonRpcClient) -> None:
    """
    Sync snippet that walks us through creating a transaction with a path.

    Args:
        client: The network client to use to send the request.
    """
    wallet = generate_faucet_wallet(client, debug=True)
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

    path_response = client.request(path_request)
    print(path_response)

    paths = path_response.result["alternatives"][0]["paths_computed"]
    print(paths)

    payment_tx = Payment(
        account=wallet.classic_address,
        amount=destination_amount,
        destination=destination_account,
        paths=paths,
    )

    print("signed: ", safe_sign_and_autofill_transaction(payment_tx, wallet, client))


# uncomment the lines below to run the snippet
# client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
# create_tx_with_paths(client)
