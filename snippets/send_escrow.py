"""Example of how we can set up an escrow"""
from datetime import datetime

from xrpl.account import get_balance
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountObjects
from xrpl.models.transactions import EscrowCreate, EscrowFinish
from xrpl.transaction.reliable_submission import submit_and_wait
from xrpl.utils import datetime_to_ripple_time
from xrpl.wallet import generate_faucet_wallet

# References
# - https://xrpl.org/escrowcreate.html#escrowcreate
# - https://xrpl.org/escrowfinish.html#escrowfinish
# - https://xrpl.org/account_objects.html#account_objects

# Create a client to connect to the test network
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# Creating two wallets to send money between
wallet1 = generate_faucet_wallet(client, debug=True)
wallet2 = generate_faucet_wallet(client, debug=True)

# Both balances should be zero since nothing has been sent yet
print("Balances of wallets before Escrow tx was created:")
print(get_balance(wallet1.classic_address, client))
print(get_balance(wallet2.classic_address, client))

# Create a finish time (2 seconds from current time)
finish_after = datetime_to_ripple_time(datetime.now()) + 2

# Create an EscrowCreate transaction, then sign, autofill, and send it
create_tx = EscrowCreate(
    account=wallet1.classic_address,
    destination=wallet2.classic_address,
    amount="1000000",
    finish_after=finish_after,
)

create_escrow_response = submit_and_wait(create_tx, wallet1, client)
print(create_escrow_response)

# Create an AccountObjects request and have the client call it to see if escrow exists
account_objects_request = AccountObjects(account=wallet1.classic_address)
account_objects = (client.request(account_objects_request)).result["account_objects"]

print("Escrow object exists in wallet1's account:")
print(account_objects)

# Create an EscrowFinish transaction, then sign, autofill, and send it
finish_tx = EscrowFinish(
    account=wallet1.classic_address,
    owner=wallet1.classic_address,
    offer_sequence=create_escrow_response.result["Sequence"],
)

submit_and_wait(finish_tx, client, wallet1)

# If escrow went through successfully, 1000000 exchanged
print("Balances of wallets after Escrow was sent:")
print(get_balance(wallet1.classic_address, client))
print(get_balance(wallet2.classic_address, client))
