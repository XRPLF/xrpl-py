# xrpl-py

A pure Python implementation for interacting with the XRP Ledger, the `xrpl-py` library simplifies the hardest parts of XRP Ledger interaction, like serialization and transaction signing, by providing native Python methods and models for [XRP Ledger transactions](https://xrpl.org/transaction-formats.html) and core server [API](https://xrpl.org/api-conventions.html) ([`rippled`](https://github.com/ripple/rippled)) objects.



```py
# create a network client
>>> from xrpl.clients.json_rpc_client import JsonRpcClient
>>> client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
# create a wallet on the testnet
>>> from xrpl.wallet import generate_faucet_wallet
>>> test_wallet = generate_faucet_wallet(client)
>>> print(test_wallet)
seed: shA5izLnSNFxNwGMV1ar6WJnnsNbo
pub_key: 029234B7F15318156A762E5411E6E3FE5A170D49FFC50286C38D7E68AE16B7B412
priv_key: 0031DFF36F8F22287BAD4137DA182635F3E0F0F510698E50A3039BB5CE170B941A
classic_address: rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz
# look up account info
>>> from xrpl.models.requests.account_info import AccountInfo
>>> acct_info = AccountInfo(
...         account="rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz",
...         ledger_index="current",
...         queue=True,
...         strict=True,
...     )
>>> response = client.request(acct_info)
>>> result = response.result
>>> import json
>>> print(json.dumps(result["account_data"], indent=4, sort_keys=True))
{
    "Account": "rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz",
    "Balance": "1000000000",
    "Flags": 0,
    "LedgerEntryType": "AccountRoot",
    "OwnerCount": 0,
    "PreviousTxnID": "E9100102A987CCB133BDDD141162A8AA90D6CE2FC7D8322D207D4E23E0077591",
    "PreviousTxnLgrSeq": 16034060,
    "Sequence": 16034060,
    "index": "519467AED2AFDBA971BE5E14EA0B622BF4E1C6CF1859AA91675E1EE061F7EBC7"
}
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

* A network client — See [`xrpl.clients`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.clients.html) for more information.
* Methods for inspecting accounts — See [XRPL Account Methods](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.account.html) for more information.
* Codecs for encoding and decoding addresses and other objects — See [Core Codecs](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.core.html) for more information.

## [➡️ Reference Documentation](https://xrpl-py.readthedocs.io/en/latest/)

See the complete [`xrpl-py` reference documentation on Read the Docs](https://xrpl-py.readthedocs.io/en/latest/index.html).


## Usage

The following sections describe some of the most commonly used modules in the `xrpl-py` library and provide sample code.

### Network client

Use the `xrpl.clients` library to create a network client for connecting to the XRP Ledger.

```py
from xrpl.clients.json_rpc_client import JsonRpcClient
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)
```

### Manage keys and wallets

#### `xrpl.wallet`

Use the [`xrpl.wallet`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.wallet.html) module to create a wallet from a given seed or or via a [Testnet faucet](https://xrpl.org/xrp-testnet-faucet.html).

To create a wallet from a seed (in this case, the value generated using [`xrpl.keypairs`](#xrpl-keypairs)):

```py
wallet_from_seed = xrpl.wallet.Wallet(seed)
print(wallet_from_seed)

# print output
seed: sEdTNFV69uSpcHpCppa6VzMvmC68CVY
pub_key: ED46949E414A3D6D758D347BAEC9340DC78F7397FEE893132AAF5D56E4D7DE77B0
priv_key: EDE65EE7882847EF5345A43BFB8E6F5EEC60F45461696C384639B99B26AAA7A5CD
classic_address: rG5ZvYsK5BPi9f1Nb8mhFGDTNMJhEhufn6
```

To create a wallet from a Testnet faucet:

```py
test_wallet = generate_faucet_wallet(client)
test_account = test_wallet.classic_address
print("Classic address:\n", test_account)

# print output
Classic address:

 rEQB2hhp3rg7sHj6L8YyR4GG47Cb7pfcuw
```

#### `xrpl.core.keypairs`

Use the [`xrpl.core.keypairs`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.core.keypairs.html#module-xrpl.core.keypairs) module to generate seeds and derive keypairs and addresses from those seed values.

Here's an example of how to generate a `seed` value and derive an [XRP Ledger "classic" address](https://xrpl.org/cryptographic-keys.html#account-id-and-address) from that seed.


```py
from xrpl.core import keypairs
seed = keypairs.generate_seed()
public, private = keypairs.derive_keypair(seed)
test_account = keypairs.derive_classic_address(public)
print(f"Here's the public key:\n", public)
print(f"Here's the private key:\n", private +  "\nStore this in a secure place.")
```

**Note:** You can use `xrpl.core.keypairs.sign` to sign transactions but `xrpl-py` also provides explicit methods for safely signing and submitting transactions. See [Transaction Signing](#transaction-signing) and [XRPL Transaction Methods](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html#module-xrpl.transaction) for more information.


### Serialize and sign transactions

To securely submit transactions to the XRP Ledger, you need to first serialize data from JSON and other formats into the [XRP Ledger's canonical format](https://xrpl.org/serialization.html), then to [authorize the transaction](https://xrpl.org/transaction-basics.html#authorizing-transactions) by digitally [signing it](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.core.keypairs.html?highlight=sign#xrpl.core.keypairs.sign) with the account's private key. The `xrpl-py` library provides several methods to simplify this process.


Use the [`xrpl.transaction`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html) module to sign and submit transactions. The module offers three ways to do this:

* [`safe_sign_and_submit_transaction`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html#xrpl.transaction.safe_sign_and_submit_transaction) — Signs a transaction locally, then submits it to the XRP Ledger. This method does not implement [reliable transaction submission](https://xrpl.org/reliable-transaction-submission.html#reliable-transaction-submission) best practices, so only use it for development or testing purposes.

* [`safe_sign_transaction`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html#xrpl.transaction.safe_sign_transaction) — Signs a transaction locally. This method **does  not** submit the transaction to the XRP Ledger.

* [`send_reliable_submission`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html#xrpl.transaction.send_reliable_submission) — An implementation of the [reliable transaction submission guidelines](https://xrpl.org/reliable-transaction-submission.html#reliable-transaction-submission), this method signs a transaction locally, submits the transaction to the XRP Ledger, and then verifies that it has been included in a validated ledger (or has failed to do so). Use this method to submit transactions for production purposes.


```py
from xrpl.models.transactions import Payment
from xrpl.transaction import send_reliable_submission
from xrpl.ledger import get_latest_validated_ledger_sequence

current_validated_ledger = get_latest_validated_ledger_sequence(client)

# prepare the transaction
# the amount is expressed in drops, not XRP
# see https://xrpl.org/basic-data-types.html#specifying-currency-amounts
my_tx_payment = Payment(
    account="rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz",
    amount="2200000",
    destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
    last_ledger_sequence=current_validated_ledger + 20,
    sequence=test_wallet.next_sequence_num,
    fee="10",
)
# sign the transaction
my_tx_payment_signed = safe_sign_transaction(my_tx_payment,test_wallet)

# submit the transaction
tx_response = send_reliable_submission(my_tx_payment, test_wallet, client)
```

#### Get fee from the XRP Ledger


In most cases, you can specify the minimum [transaction cost](https://xrpl.org/transaction-cost.html#current-transaction-cost) of `"10"` for the `fee` field unless you have a strong reason not to. But if you want to get the [current load-balanced transaction cost](https://xrpl.org/transaction-cost.html#current-transaction-cost) from the network, you can use the `get_fee` function:

```py
from xrpl.ledger import get_fee

FEE = get_fee(client)
print(FEE)

# print output
10
```

#### Auto-filled fields

The `xrpl-py` library automatically populates the `fee` and `last_ledger_sequence` fields when you create transactions. In the example above, you could omit those fields and let the library fill them in for you.

```py
from xrpl.models.transactions import Payment
from xrpl.transaction import send_reliable_submission

# prepare the transaction
# the amount is expressed in drops, not XRP
# see https://xrpl.org/basic-data-types.html#specifying-currency-amounts
my_tx_payment = Payment(
    account="rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz",
    amount="2200000",
    destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
    sequence=test_wallet.next_sequence_num,
)

# sign the transaction
my_tx_payment_signed = safe_sign_transaction(my_tx_payment,test_wallet)

# submit the transaction
tx_response = send_reliable_submission(my_tx_payment, test_wallet, client)

print(my_tx_payment)
Payment(account='rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz', transaction_type=<TransactionType.PAYMENT: 'Payment'>, fee=10000, sequence=16034065, account_txn_id=None, flags=0, last_ledger_sequence=10268600, memos=None, signers=None, source_tag=None, signing_pub_key=None, txn_signature=None, amount='2200000', destination='rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe', destination_tag=None, invoice_id=None, paths=None, send_max=None, deliver_min=None)
```


### Encode addresses

Use the [`xrpl.core.addresscodec`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.core.addresscodec.html) to encode and decode addresses into and from the ["classic" and X-address formats](https://xrpl.org/accounts.html#addresses).

```py
# convert classic address to x-address
>>> from xrpl.core import addresscodec
>>> tesnet_xaddress = addresscodec.classic_address_to_xaddress("rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz", tag=0, is_test_network=True)
>>> print(tesnet_xaddress)
T7QDemmxnuN7a52A62nx2fxGPWcRahLCf3qaswfrsNW9Lps
```


## Contributing

If you want to contribute to this project, see [CONTRIBUTING.md].


## License

The `xrpl-py` library is licensed under the ISC License. See [LICENSE] for more information.



[CONTRIBUTING.md]: CONTRIBUTING.md
[LICENSE]: LICENSE
