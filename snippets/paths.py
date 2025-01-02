"""Example of how to find the best path to trade with"""

from xrpl.clients import WebsocketClient
from xrpl.models import IssuedCurrencyAmount, PathFind, Payment
from xrpl.models.requests import PathFindSubcommand
from xrpl.transaction import autofill_and_sign
from xrpl.wallet import generate_faucet_wallet

# References
# - https://xrpl.org/paths.html#paths
# - https://xrpl.org/ripple_path_find.html#ripple_path_find
# Prerequisites for this snippet. Please verify these conditions after a reset of the
# test network:
# - destination_account must have a trust line with the destination_amount.issuer
# - There must be appropriate DEX Offers or XRP/TST AMM for the cross-currency exchange

# Create a client to connect to the test network
# PathFind RPC requires the use of a Websocket client only

with WebsocketClient("wss://s.altnet.rippletest.net:51233") as client:
    # Creating wallet to send money from
    wallet = generate_faucet_wallet(client, debug=True)

    # Create account and amount variables for later transaction
    destination_account = "rJPeZVPty1bXXbDR9oKscg2irqABr7sP3t"
    destination_amount = IssuedCurrencyAmount(
        value="0.001",
        currency="TST",
        issuer="rP9jPyP5kyvFRb6ZiRghAGw5u8SGAmU4bd",
    )

    # Create a RipplePathFind request and have the client call it
    path_request = PathFind(
        subcommand=PathFindSubcommand.CREATE,
        source_account=wallet.address,
        destination_account=destination_account,
        destination_amount=destination_amount,
    )
    path_response = client.request(path_request)
    print(path_response)

    # Extract out paths from the RipplePathFind response
    paths = path_response.result["alternatives"][0]["paths_computed"]
    print(paths)

    # Create a Payment to send money from wallet to destination_account using path
    payment_tx = Payment(
        account=wallet.address,
        amount=destination_amount,
        destination=destination_account,
        paths=paths,
    )

    print("signed: ", autofill_and_sign(payment_tx, client, wallet))
