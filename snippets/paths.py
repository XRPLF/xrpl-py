"""Example of ripple_path_find request using trustlines and rippling"""

from xrpl.clients import JsonRpcClient
from xrpl.models import AccountSet, TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import RipplePathFind
from xrpl.models.transactions.account_set import AccountSetAsfFlag
from xrpl.transaction import submit_and_wait
from xrpl.wallet import generate_faucet_wallet

# Note: This test is inspired from a unit test titled `indirect_paths_path_find` in the
# rippled C++ codebase (Path_test.cpp)
# https://github.com/XRPLF/rippled/blob/d9bd75e68326861fb38fd5b27d47da1054a7fc3b/src/test/app/Path_test.cpp#L683

# Create a client to connect to the test network
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# Creating wallet to send money from
# these wallets will have 100 testnet XRP
alice = generate_faucet_wallet(client, debug=True)
bob = generate_faucet_wallet(client, debug=True)
carol = generate_faucet_wallet(client, debug=True)

# send AccountSet transaction with asfDefaultRipple turned on
# this enables rippling on all trustlines through these accounts.
submit_and_wait(
    AccountSet(account=alice.address, set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE),
    client,
    alice,
)

submit_and_wait(
    AccountSet(account=bob.address, set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE),
    client,
    bob,
)

submit_and_wait(
    AccountSet(account=carol.address, set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE),
    client,
    carol,
)

# set up trustlines from bob -> alice, carol -> bob to transfer IssuedCurrency `USD`
submit_and_wait(
    TrustSet(
        account=bob.address,
        limit_amount=IssuedCurrencyAmount(
            currency="USD", issuer=alice.address, value="1000"
        ),
    ),
    client,
    bob,
)
submit_and_wait(
    TrustSet(
        account=carol.address,
        limit_amount=IssuedCurrencyAmount(
            currency="USD", issuer=bob.address, value="1000"
        ),
    ),
    client,
    carol,
)

# Perform path find
# Note: Rippling allows IssuedCurrencies with identical currency-codes,
# but different (ex: alice, bob and carol) issuers to settle their transfers.
# Docs: https://xrpl.org/docs/concepts/tokens/fungible-tokens/rippling
request = RipplePathFind(
    source_account=alice.classic_address,
    source_currencies=[
        IssuedCurrencyAmount(currency="USD", issuer=alice.address, value="1000")
    ],
    destination_account=carol.classic_address,
    destination_amount=IssuedCurrencyAmount(
        currency="USD", issuer=carol.classic_address, value="5"
    ),
)
response = client.request(request)

# Check the results
paths = response.result["alternatives"]
assert len(paths) > 0, "No paths found"

print("Paths discovered by ripple_path_find RPC:")
print(paths)

# Check if the path includes bob
# the "paths_computed" field uses a 2-D matrix representation as detailed here:
# https://xrpl.org/docs/concepts/tokens/fungible-tokens/paths#path-specifications
path = paths[0]["paths_computed"][0][0]
assert path["account"] == bob.classic_address, "Path does not include bob"

# Check the source amount
source_amount = paths[0]["source_amount"]
assert source_amount["currency"] == "USD"
assert source_amount["issuer"] == alice.classic_address
assert float(source_amount["value"]) == 5.0

print("Test passed successfully!")
