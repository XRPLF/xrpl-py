"""Example of how we can create, update and delete oracles"""
import time

from xrpl.clients import JsonRpcClient
from xrpl.models import LedgerEntry
from xrpl.models.requests.ledger_entry import Oracle
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.oracle_delete import OracleDelete
from xrpl.models.transactions.oracle_set import OracleSet, PriceData
from xrpl.transaction.reliable_submission import submit_and_wait
from xrpl.utils import str_to_hex
from xrpl.wallet import generate_faucet_wallet

# Create a client to connect to the dev-network
client = JsonRpcClient("https://s.devnet.rippletest.net:51234")

wallet = generate_faucet_wallet(client, debug=True)


_PROVIDER = str_to_hex("provider")
_ASSET_CLASS = str_to_hex("currency")
_ORACLE_DOC_ID = 1

create_tx = OracleSet(
    account=wallet.address,
    oracle_document_id=_ORACLE_DOC_ID,
    provider=_PROVIDER,
    asset_class=_ASSET_CLASS,
    last_update_time=int(time.time()),
    price_data_series=[
        PriceData(base_asset="XRP", quote_asset="USD", asset_price=740, scale=1),
        PriceData(base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2),
    ],
)

response = submit_and_wait(create_tx, client, wallet)

if response.status != ResponseStatus.SUCCESS:
    print("Create Oracle operation failed, recieved the following response")
    print(response)

# update the oracle data
update_tx = OracleSet(
    account=wallet.address,
    oracle_document_id=_ORACLE_DOC_ID,
    last_update_time=int(time.time()),
    price_data_series=[
        PriceData(base_asset="XRP", quote_asset="USD", asset_price=742, scale=1),
        PriceData(base_asset="BTC", quote_asset="EUR", asset_price=103, scale=2),
    ],
)
response = submit_and_wait(update_tx, client, wallet)

if response.status != ResponseStatus.SUCCESS:
    print("Update Oracle operation failed, recieved the following response")
    print(response)

ledger_entry_req = LedgerEntry(
    oracle=Oracle(account=wallet.address, oracle_document_id=_ORACLE_DOC_ID)
)
response = client.request(ledger_entry_req)

if response.status != ResponseStatus.SUCCESS:
    print("Test failed: Oracle Ledger Entry is not present")
    print(response)


# delete the oracle
delete_tx = OracleDelete(account=wallet.address, oracle_document_id=_ORACLE_DOC_ID)
response = submit_and_wait(delete_tx, client, wallet)

if response.status != ResponseStatus.SUCCESS:
    print("Delete Oracle operation failed, recieved the following response")
    print(response)

ledger_entry_req = LedgerEntry(
    oracle=Oracle(account=wallet.address, oracle_document_id=_ORACLE_DOC_ID)
)
response = client.request(ledger_entry_req)

if response.status != ResponseStatus.ERROR:
    print("Test failed: Oracle Ledger Entry has not been deleted")
    print(response)
