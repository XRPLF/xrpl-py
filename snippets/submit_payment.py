"""Example of how to send a transaction and see its validation response"""

from xrpl.account import get_balance
from xrpl.clients import JsonRpcClient
from xrpl.models import Payment, Tx
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops
from xrpl.wallet import generate_faucet_wallet

# References:
# - https://xrpl.org/reliable-transaction-submission.html
# - https://xrpl.org/send-xrp.html
# - https://xrpl.org/look-up-transaction-results.html

# Create a client to connect to the test network
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# Creating two wallets to send money between
wallet = generate_faucet_wallet(client, debug=True)
destination = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"

# Both balances should be zero since nothing has been sent yet
print("Balances of wallets before Payment tx")
print(get_balance(wallet.address, client))
print(get_balance(destination, client))

# Create a Payment transaction
payment_tx = Payment(
    account=wallet.address,
    amount=xrp_to_drops(50),
    destination=destination,
)

# Signs, autofills, and submits transaction and waits for response
# (validated or rejected)
payment_response = submit_and_wait(payment_tx, client, wallet)
print("Transaction was submitted")

# Create a Transaction request to see transaction
tx_response = client.request(Tx(transaction=payment_response.result["hash"]))

# Check validated field on the transaction
print("Validated:", tx_response.result["validated"])

# Check balances after 50 XRP was sent from wallet to destination
print("Balances of wallets after Payment tx:")
print(get_balance(wallet.address, client))
print(get_balance(destination, client))
