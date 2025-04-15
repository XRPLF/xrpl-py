"""Example of how we can setting a regular key"""

from xrpl.account import get_balance
from xrpl.clients import JsonRpcClient
from xrpl.models import Payment, SetRegularKey
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops
from xrpl.wallet import Wallet, generate_faucet_wallet

# References
# - https://xrpl.org/assign-a-regular-key-pair.html#assign-a-regular-key-pair
# - https://xrpl.org/setregularkey.html#setregularkey
# - https://xrpl.org/change-or-remove-a-regular-key-pair.html

# Create a client to connect to the test network
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# Creating two wallets to send money between
wallet = generate_faucet_wallet(client, debug=True)
destination = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"
regular_key_wallet = Wallet.create()

# Both balances should be zero since nothing has been sent yet
print("Balances before payment:")
print(get_balance(wallet.address, client))
print(get_balance(destination, client))

# Assign key pair (regular_key_wallet) to wallet using SetRegularKey transaction
tx = SetRegularKey(account=wallet.address, regular_key=regular_key_wallet.address)

set_regular_key_response = submit_and_wait(tx, client, wallet)

print("Response for successful SetRegularKey tx:")
print(set_regular_key_response)

# Since regular_key_wallet is linked to wallet,
# wallet can send payment to destination and have regular_key_wallet sign it
payment = Payment(
    account=wallet.address,
    destination=destination,
    amount=xrp_to_drops(50),
)

payment_response = submit_and_wait(payment, client, regular_key_wallet)

print("Response for tx signed using Regular Key:")
print(payment_response)

# Balance after sending 50 XRP from wallet1 to wallet2
print("Balances after payment:")
print(get_balance(wallet.address, client))
print(get_balance(destination, client))
