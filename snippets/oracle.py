"""Example of how we can create, update and delete oracles"""
import time

from xrpl.clients import JsonRpcClient
from xrpl.models.transactions.delete_oracle import OracleDelete
from xrpl.models.transactions.set_oracle import OracleSet, PriceData
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
# TODO: Keshava
# print(response.result['meta']['TransactionResult'] == 'tesSUCCESS') # does not work
print(
    "Result of SetOracle transaction: " + response.result["meta"]["TransactionResult"]
)

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

print(
    "Result of the Update Oracle transaction: "
    + response.result["meta"]["TransactionResult"]
)


# delete the oracle
delete_tx = OracleDelete(account=wallet.address, oracle_document_id=_ORACLE_DOC_ID)
response = submit_and_wait(delete_tx, client, wallet)

print(
    "Result of DeleteOracle transaction: "
    + response.result["meta"]["TransactionResult"]
)
