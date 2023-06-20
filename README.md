[![Documentation Status](https://readthedocs.org/projects/xrpl-py/badge)](https://xrpl-py.readthedocs.io/)

# xrpl-py

A pure Python implementation for interacting with the XRP Ledger, the `xrpl-py` library simplifies the hardest parts of XRP Ledger interaction, like serialization and transaction signing, by providing native Python methods and models for [XRP Ledger transactions](https://xrpl.org/transaction-formats.html) and core server [API](https://xrpl.org/api-conventions.html) ([`rippled`](https://github.com/ripple/rippled)) objects.



```py
# create a network client
from xrpl.clients import JsonRpcClient
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# create a wallet on the testnet
from xrpl.wallet import generate_faucet_wallet
test_wallet = generate_faucet_wallet(client)
print(test_wallet)
public_key: ED3CC1BBD0952A60088E89FA502921895FC81FBD79CAE9109A8FE2D23659AD5D56
private_key: -HIDDEN-
classic_address: rBtXmAdEYcno9LWRnAGfT9qBxCeDvuVRZo

# look up account info
from xrpl.models import AccountInfo
acct_info = AccountInfo(
    account="rBtXmAdEYcno9LWRnAGfT9qBxCeDvuVRZo",
    ledger_index="current",
    queue=True,
    strict=True,
)
response = client.request(acct_info)
result = response.result
import json
print(json.dumps(result["account_data"], indent=4, sort_keys=True))
# {
#     "Account": "rBtXmAdEYcno9LWRnAGfT9qBxCeDvuVRZo",
#     "Balance": "1000000000",
#     "Flags": 0,
#     "LedgerEntryType": "AccountRoot",
#     "OwnerCount": 0,
#     "PreviousTxnID": "73CD4A37537A992270AAC8472F6681F44E400CBDE04EC8983C34B519F56AB107",
#     "PreviousTxnLgrSeq": 16233962,
#     "Sequence": 16233962,
#     "index": "FD66EC588B52712DCE74831DCB08B24157DC3198C29A0116AA64D310A58512D7"
# }
```

[![Downloads](https://pepy.tech/badge/xrpl-py/month)](https://pepy.tech/project/xrpl-py/month)
[![Contributors](https://img.shields.io/github/contributors/xpring-eng/xrpl-py.svg)](https://github.com/xpring-eng/xrpl-py/graphs/contributors)

## Installation and supported versions

The `xrpl-py` library is available on [PyPI](https://pypi.org/). Install with `pip`:


```
pip3 install xrpl-py
```

The library supports [Python 3.7](https://www.python.org/downloads/) and later.

[![Supported Versions](https://img.shields.io/pypi/pyversions/xrpl-py.svg)](https://pypi.org/project/xrpl-py)


## Features

Use `xrpl-py` to build Python applications that leverage the [XRP Ledger](https://xrpl.org/). The library helps with all aspects of interacting with the XRP Ledger, including:

* Key and wallet management
* Serialization
* Transaction Signing

`xrpl-py` also provides:

* A network client — See [`xrpl.clients`](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.clients.html) for more information.
* Methods for inspecting accounts — See [XRPL Account Methods](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.account.html) for more information.
* Codecs for encoding and decoding addresses and other objects — See [Core Codecs](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.core.html) for more information.

## [➡️ Reference Documentation](https://xrpl-py.readthedocs.io/en/stable/)

See the complete [`xrpl-py` reference documentation on Read the Docs](https://xrpl-py.readthedocs.io/en/stable/index.html).


## Usage

The following sections describe some of the most commonly used modules in the `xrpl-py` library and provide sample code.

### Network client

Use the `xrpl.clients` library to create a network client for connecting to the XRP Ledger.

```py
from xrpl.clients import JsonRpcClient
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)
```

### Manage keys and wallets

#### `xrpl.wallet`

Use the [`xrpl.wallet`](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.wallet.html) module to create a wallet from a given seed or or via a [Testnet faucet](https://xrpl.org/xrp-testnet-faucet.html).

To create a wallet from a seed (in this case, the value generated using [`xrpl.keypairs`](#xrpl-keypairs)):

```py
wallet_from_seed = xrpl.wallet.Wallet(seed, 0)
print(wallet_from_seed)
# pub_key: ED46949E414A3D6D758D347BAEC9340DC78F7397FEE893132AAF5D56E4D7DE77B0
# priv_key: -HIDDEN-
# classic_address: rG5ZvYsK5BPi9f1Nb8mhFGDTNMJhEhufn6
```

To create a wallet from a Testnet faucet:

```py
test_wallet = generate_faucet_wallet(client)
test_account = test_wallet.classic_address
print("Classic address:", test_account)
# Classic address: rEQB2hhp3rg7sHj6L8YyR4GG47Cb7pfcuw
```

#### `xrpl.core.keypairs`

Use the [`xrpl.core.keypairs`](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.core.keypairs.html#module-xrpl.core.keypairs) module to generate seeds and derive keypairs and addresses from those seed values.

Here's an example of how to generate a `seed` value and derive an [XRP Ledger "classic" address](https://xrpl.org/cryptographic-keys.html#account-id-and-address) from that seed.


```py
from xrpl.core import keypairs
seed = keypairs.generate_seed()
public, private = keypairs.derive_keypair(seed)
test_account = keypairs.derive_classic_address(public)
print("Here's the public key:")
print(public)
print("Here's the private key:")
print(private)
print("Store this in a secure place!")
# Here's the public key:
# ED3CC1BBD0952A60088E89FA502921895FC81FBD79CAE9109A8FE2D23659AD5D56
# Here's the private key:
# EDE65EE7882847EF5345A43BFB8E6F5EEC60F45461696C384639B99B26AAA7A5CD
# Store this in a secure place!
```

**Note:** You can use `xrpl.core.keypairs.sign` to sign transactions but `xrpl-py` also provides explicit methods for safely signing and submitting transactions. See [Transaction Signing](#transaction-signing) and [XRPL Transaction Methods](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.transaction.html#module-xrpl.transaction) for more information.


### Serialize and sign transactions

To securely submit transactions to the XRP Ledger, you need to first serialize data from JSON and other formats into the [XRP Ledger's canonical format](https://xrpl.org/serialization.html), then to [authorize the transaction](https://xrpl.org/transaction-basics.html#authorizing-transactions) by digitally [signing it](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.core.keypairs.html?highlight=sign#xrpl.core.keypairs.sign) with the account's private key. The `xrpl-py` library provides several methods to simplify this process.


Use the [`xrpl.transaction`](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.transaction.html) module to sign and submit transactions. The module offers three ways to do this:

* [`sign_and_submit`](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.transaction.html#xrpl.transaction.sign_and_submit) — Signs a transaction locally, then submits it to the XRP Ledger. This method does not implement [reliable transaction submission](https://xrpl.org/reliable-transaction-submission.html#reliable-transaction-submission) best practices, so only use it for development or testing purposes.

* [`sign`](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.transaction.html#xrpl.transaction.sign) — Signs a transaction locally. This method **does  not** submit the transaction to the XRP Ledger.

* [`send_reliable_submission`](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.transaction.html#xrpl.transaction.send_reliable_submission) — An implementation of the [reliable transaction submission guidelines](https://xrpl.org/reliable-transaction-submission.html#reliable-transaction-submission), this method submits a signed transaction to the XRP Ledger and then verifies that it has been included in a validated ledger (or has failed to do so). Use this method to submit transactions for production purposes.


```py
from xrpl.models import Payment
from xrpl.transaction import sign, send_reliable_submission
from xrpl.ledger import get_latest_validated_ledger_sequence
from xrpl.account import get_next_valid_seq_number

current_validated_ledger = get_latest_validated_ledger_sequence(client)
wallet_sequence = get_next_valid_seq_number(test_wallet.classic_address, client)

# prepare the transaction
# the amount is expressed in drops, not XRP
# see https://xrpl.org/basic-data-types.html#specifying-currency-amounts
my_tx_payment = Payment(
    account=test_wallet.classic_address,
    amount="2200000",
    destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
    last_ledger_sequence=current_validated_ledger + 20,
    sequence=wallet_sequence,
    fee="10",
)
# sign the transaction
my_tx_payment_signed = sign(my_tx_payment,test_wallet)

# submit the transaction
tx_response = send_reliable_submission(my_tx_payment_signed, client)
```

#### Get fee from the XRP Ledger


In most cases, you can specify the minimum [transaction cost](https://xrpl.org/transaction-cost.html#current-transaction-cost) of `"10"` for the `fee` field unless you have a strong reason not to. But if you want to get the [current load-balanced transaction cost](https://xrpl.org/transaction-cost.html#current-transaction-cost) from the network, you can use the `get_fee` function:

```py
from xrpl.ledger import get_fee
fee = get_fee(client)
print(fee)
# 10
```

#### Auto-filled fields

The `xrpl-py` library automatically populates the `fee`, `sequence` and `last_ledger_sequence` fields when you create transactions. In the example above, you could omit those fields and let the library fill them in for you.

```py
from xrpl.models import Payment
from xrpl.transaction import send_reliable_submission, autofill_and_sign
# prepare the transaction
# the amount is expressed in drops, not XRP
# see https://xrpl.org/basic-data-types.html#specifying-currency-amounts
my_tx_payment = Payment(
    account=test_wallet.classic_address,
    amount="2200000",
    destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"
)

# sign the transaction with the autofill method
# (this will auto-populate the fee, sequence, and last_ledger_sequence)
my_tx_payment_signed = autofill_and_sign(my_tx_payment, test_wallet, client)
print(my_tx_payment_signed)
# Payment(
#     account='rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz',
#     transaction_type=<TransactionType.PAYMENT: 'Payment'>,
#     fee='10',
#     sequence=16034065,
#     account_txn_id=None,
#     flags=0,
#     last_ledger_sequence=10268600,
#     memos=None,
#     signers=None,
#     source_tag=None,
#     signing_pub_key='EDD9540FA398915F0BCBD6E65579C03BE5424836CB68B7EB1D6573F2382156B444',
#     txn_signature='938FB22AE7FE76CF26FD11F8F97668E175DFAABD2977BCA397233117E7E1C4A1E39681091CC4D6DF21403682803AB54CC21DC4FA2F6848811DEE10FFEF74D809',
#     amount='2200000',
#     destination='rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe',
#     destination_tag=None,
#     invoice_id=None,
#     paths=None,
#     send_max=None,
#     deliver_min=None
# )

# submit the transaction
tx_response = send_reliable_submission(my_tx_payment_signed, client)
```


### Subscribe to ledger updates

You can send `subscribe` and `unsubscribe` requests only using the WebSocket network client. These request methods allow you to be alerted of certain situations as they occur, such as when a new ledger is declared.

```py
from xrpl.clients import WebsocketClient
url = "wss://s.altnet.rippletest.net/"
from xrpl.models import Subscribe, StreamParameter
req = Subscribe(streams=[StreamParameter.LEDGER])
# NOTE: this code will run forever without a timeout, until the process is killed
with WebsocketClient(url) as client:
    client.send(req)
    for message in client:
        print(message)
# {'result': {'fee_base': 10, 'fee_ref': 10, 'ledger_hash': '7CD50477F23FF158B430772D8E82A961376A7B40E13C695AA849811EDF66C5C0', 'ledger_index': 18183504, 'ledger_time': 676412962, 'reserve_base': 20000000, 'reserve_inc': 5000000, 'validated_ledgers': '17469391-18183504'}, 'status': 'success', 'type': 'response'}
# {'fee_base': 10, 'fee_ref': 10, 'ledger_hash': 'BAA743DABD168BD434804416C8087B7BDEF7E6D7EAD412B9102281DD83B10D00', 'ledger_index': 18183505, 'ledger_time': 676412970, 'reserve_base': 20000000, 'reserve_inc': 5000000, 'txn_count': 0, 'type': 'ledgerClosed', 'validated_ledgers': '17469391-18183505'}
# {'fee_base': 10, 'fee_ref': 10, 'ledger_hash': 'D8227DAF8F745AE3F907B251D40B4081E019D013ABC23B68C0B1431DBADA1A46', 'ledger_index': 18183506, 'ledger_time': 676412971, 'reserve_base': 20000000, 'reserve_inc': 5000000, 'txn_count': 0, 'type': 'ledgerClosed', 'validated_ledgers': '17469391-18183506'}
# {'fee_base': 10, 'fee_ref': 10, 'ledger_hash': 'CFC412B6DDB9A402662832A781C23F0F2E842EAE6CFC539FEEB287318092C0DE', 'ledger_index': 18183507, 'ledger_time': 676412972, 'reserve_base': 20000000, 'reserve_inc': 5000000, 'txn_count': 0, 'type': 'ledgerClosed', 'validated_ledgers': '17469391-18183507'}
```


### Asynchronous Code

This library supports Python's [`asyncio`](https://docs.python.org/3/library/asyncio.html) package, which is used to run asynchronous code. All the async code is in [`xrpl.asyncio`](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.asyncio.html) If you are writing asynchronous code, please note that you will not be able to use any synchronous sugar functions, due to how event loops are handled. However, every synchronous method has a corresponding asynchronous method that you can use.

This sample code is the asynchronous equivalent of the above section on submitting a transaction.

```py
import asyncio
from xrpl.models import Payment
from xrpl.asyncio.transaction import sign, send_reliable_submission
from xrpl.asyncio.ledger import get_latest_validated_ledger_sequence
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.asyncio.clients import AsyncJsonRpcClient

async_client = AsyncJsonRpcClient(JSON_RPC_URL)

async def submit_sample_transaction():
    current_validated_ledger = await get_latest_validated_ledger_sequence(async_client)
    wallet_sequence = await get_next_valid_seq_number(test_wallet.classic_address, async_client)

    # prepare the transaction
    # the amount is expressed in drops, not XRP
    # see https://xrpl.org/basic-data-types.html#specifying-currency-amounts
    my_tx_payment = Payment(
        account=test_wallet.classic_address,
        amount="2200000",
        destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
        last_ledger_sequence=current_validated_ledger + 20,
        sequence=wallet_sequence,
        fee="10",
    )
    # sign the transaction
    my_tx_payment_signed = await sign(my_tx_payment,test_wallet)

    # submit the transaction
    tx_response = await send_reliable_submission(my_tx_payment_signed, async_client)

asyncio.run(submit_sample_transaction())
```

### Encode addresses

Use [`xrpl.core.addresscodec`](https://xrpl-py.readthedocs.io/en/stable/source/xrpl.core.addresscodec.html) to encode and decode addresses into and from the ["classic" and X-address formats](https://xrpl.org/accounts.html#addresses).

```py
# convert classic address to x-address
from xrpl.core import addresscodec
testnet_xaddress = (
    addresscodec.classic_address_to_xaddress(
        "rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz",
        tag=0,
        is_test_network=True,
    )
)
print(testnet_xaddress)
# T7QDemmxnuN7a52A62nx2fxGPWcRahLCf3qaswfrsNW9Lps
```


## Contributing

If you want to contribute to this project, see [CONTRIBUTING.md].

### Mailing Lists

We have a low-traffic mailing list for announcements of new `xrpl-py` releases. (About 1 email per week)

+ [Subscribe to xrpl-announce](https://groups.google.com/g/xrpl-announce)

If you're using the XRP Ledger in production, you should run a [rippled server](https://github.com/ripple/rippled) and subscribe to the ripple-server mailing list as well.

+ [Subscribe to ripple-server](https://groups.google.com/g/ripple-server)

### Code Samples
- For samples of common use cases, see the [XRPL.org Code Samples](https://xrpl.org/code-samples.html) page.
- You can also browse those samples [directly on GitHub](https://github.com/XRPLF/xrpl-dev-portal/tree/master/content/_code-samples).

### Report an issue

Experienced an issue? Report it [here](https://github.com/XRPLF/xrpl-py/issues/new).

## License

The `xrpl-py` library is licensed under the ISC License. See [LICENSE] for more information.



[CONTRIBUTING.md]: CONTRIBUTING.md
[LICENSE]: LICENSE
