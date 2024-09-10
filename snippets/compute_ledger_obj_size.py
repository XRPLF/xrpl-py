"""Example of how we can see a transaction that was validated on the ledger"""
from xrpl.clients import JsonRpcClient
from xrpl.models import Ledger, Tx
from xrpl.models.response import ResponseStatus

# References
# - https://xrpl.org/look-up-transaction-results.html
# - https://xrpl.org/parallel-networks.html#parallel-networks
# - https://xrpl.org/tx.html

# Create a client to connect to the main network
client = JsonRpcClient("https://xrplcluster.com/")

# Create a Ledger request and have the client call it
ledger_request = Ledger(ledger_index="validated", transactions=True)
ledger_response = client.request(ledger_request)
if ledger_response.status != ResponseStatus.SUCCESS:
    print("Could not retrieve ledger successfully")
    exit()

current_ledger_index = ledger_response.result['ledger_index']

# accumulator variable to store all accounts
recent_accounts = set()

# number of ledgers under consideration
ledger_window = 10

# request the latest 10 validated ledgers
for lgr in range(current_ledger_index - ledger_window, current_ledger_index + 1):
    ledger_request = Ledger(ledger_index=lgr, transactions=True)
    ledger_response = client.request(ledger_request)
    if ledger_response.status != ResponseStatus.SUCCESS:
        print("Could not retrieve ledger index: " + str(lgr) + " successfully")

    # Extract out transactions from the ledger response
    transactions = ledger_response.result["ledger"]["transactions"]

    for tx in transactions:
        # Create a Transaction request and have the client call it
        tx_response = client.request(Tx(transaction=tx))
        if tx_response.status == ResponseStatus.SUCCESS:
            recent_accounts.add(tx_response.result['tx_json']['Account'])
        else:
            print("Transaction could not be retrieved successfully")
    print("Processed ledger index " + str(lgr) + " completely")

print("Number of unique accuonts under consideration: " + str(len(recent_accounts)))
print(recent_accounts)
