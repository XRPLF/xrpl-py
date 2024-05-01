"""Snippet demonstrates obtaining aggregate statistics of PriceOracles"""
import time

from xrpl.clients import JsonRpcClient
from xrpl.models.requests.get_aggregate_price import GetAggregatePrice, OracleInfo
from xrpl.models.transactions.oracle_set import OracleSet, PriceData
from xrpl.transaction.reliable_submission import submit_and_wait
from xrpl.utils import str_to_hex
from xrpl.wallet import generate_faucet_wallet

# Create a client to connect to the dev-network
client = JsonRpcClient("https://s.devnet.rippletest.net:51234")

_PROVIDER = str_to_hex("provider")
_ASSET_CLASS = str_to_hex("currency")

# list stores the (account, oracle_document_id) information
oracle_info = []

for i in range(10):
    # new (pseudo-random) addresses are generated
    wallet = generate_faucet_wallet(client, debug=True)
    create_tx = OracleSet(
        account=wallet.address,
        oracle_document_id=i,
        provider=_PROVIDER,
        asset_class=_ASSET_CLASS,
        last_update_time=int(time.time()),
        price_data_series=[
            PriceData(
                base_asset="XRP", quote_asset="USD", asset_price=740 + i, scale=1
            ),
            PriceData(
                base_asset="BTC", quote_asset="EUR", asset_price=100 + i, scale=2
            ),
        ],
    )

    response = submit_and_wait(create_tx, client, wallet)

    # store the (account, oracle_document_id) for future use
    oracle_info.append(OracleInfo(account=wallet.address, oracle_document_id=i))

get_agg_request = GetAggregatePrice(
    base_asset="XRP", quote_asset="USD", oracles=oracle_info
)
response = client.request(get_agg_request)
print(response)
