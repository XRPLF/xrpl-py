from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import AccountSet, AccountSetFlag
from xrpl.transaction import safe_sign_and_autofill_transaction, send_reliable_submission, autofill, safe_sign_transaction
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.requests import AccountInfo

# This code snippet will enable 'Require Destination Tags' on an account
# A funded account on the testnet is provided for testing purposes
# https://xrpl.org/require-destination-tags.html#require-destination-tags
# https://xrpl.org/source-and-destination-tags.html

lsfRequireDestTag = 131072

# Connect to a testnet node
print("Connecting to Testnet...")
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)

# Get account credentials from the Testnet Faucet
print("Requesting address from the Testnet faucet...")
test_wallet = generate_faucet_wallet(client=client)
myAddr = test_wallet.classic_address

# Construct AccountSet transaction with "ASF_REQUIRE_DEST" flag which will enable 'Require Destination Tags'
enable_destination_tag_tx = AccountSet(
    account=myAddr,
    set_flag=AccountSetFlag.ASF_REQUIRE_DEST
)

# Sign the transaction
enable_destination_tag_tx_signed = safe_sign_and_autofill_transaction(enable_destination_tag_tx, client=client, wallet=test_wallet)
submit_tx = send_reliable_submission(client=client, transaction=enable_destination_tag_tx_signed)
submit_tx = submit_tx.result
print(f"\n Submit result: {submit_tx['meta']['TransactionResult']}")
print(f"    Tx content: {submit_tx}")

# Verify Account Settings via AccountInfo request
get_acc_flag = client.request(
    AccountInfo(account=myAddr)
)

if get_acc_flag.result['account_data']['Flags'] & lsfRequireDestTag:
    print(f"\nRequire Destination Tag is ENABLED on {myAddr}")
else:
    print(f"\nRequire Destination Tag is DISABLED on {myAddr}")
