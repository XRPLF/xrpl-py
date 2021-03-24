# xrpl-py

A pure Python implementation for interacting with the XRP Ledger, the `xrpl-py` library simplifies the hardest parts of XRP Ledger interaction, like serialization and transaction signing, by providing native Python methods and models for [XRP Ledger](https://xrpl.org/ledger-data-formats.html) and core server [API](https://xrpl.org/api-conventions.html) ([`rippled`](https://github.com/ripple/rippled)) objects.



```py
>>> import xrpl
# create a network client
>>> from xrpl.clients.json_rpc_client import JsonRpcClient
>>> JSON_RPC_URL_TESTNET = "https://s.altnet.rippletest.net:51234/"
>>> JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL_TESTNET)
# create a wallet on the testnet
>>> from xrpl.wallet import generate_faucet_wallet, Wallet
>>> TESTNET_WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)
>>> TESTNET_CLASSIC_ACCOUNT = TESTNET_WALLET.classic_address
>>> print(TESTNET_CLASSIC_ACCOUNT)
ra9cjuPRq7tmR3Uin3y6fUPKLZ317JLvbN
# look up account info
>>> from xrpl.models.requests.account_info import AccountInfo
>>> acct_info = AccountInfo(
...         account=TESTNET_CLASSIC_ACCOUNT,
...         ledger_index="current",
...         queue=True,
...         strict=True,
...     )
>>> response = JSON_RPC_CLIENT.request(acct_info)
>>> result = response.result
>>> import json
>>> print(json.dumps(result["account_data"], indent=4, sort_keys=True))
{
    "Account": "ra9cjuPRq7tmR3Uin3y6fUPKLZ317JLvbN",
    "Balance": "1000000000",
    "Flags": 0,
    "LedgerEntryType": "AccountRoot",
    "OwnerCount": 0,
    "PreviousTxnID": "9E2F0CCE94B6D0CF6B802C248080B7502728584731D17A8AB9EE9938433A2F54",
    "PreviousTxnLgrSeq": 16007556,
    "Sequence": 16007556,
    "index": "EEE14A3994B4067813CEF0E6B94F1FCD2B66204DEF1B8DB6E3E6909770132F7B"
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
* Methods for insepcting accounts — See [XRPL Account Methods](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.account.html) for more information.
* Codecs for encoding and decoding addresses and other objects — See [Core Codecs](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.core.html) for more information.


## Usage

The following sections describe some of the most commonly used modules in the `xrpl-py` library and provide sample code.

For complete reference documentation, see the [`xrpl-py` docs](https://xrpl-py.readthedocs.io/en/latest/index.html).

### Network client

Use the `xrpl.clients` library to create a network client for connecting to the XRP Ledger.

```py
from xrpl.clients.json_rpc_client import JsonRpcClient
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)
```

### Manage keys and wallets

#### `xrpl.wallet`

Use the [`xrpl.wallet`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.wallet.html) module to create a wallet from a given seed or or via a [Testnet faucet](https://xrpl.org/xrp-testnet-faucet.html).

To create a wallet from a seed (in this case, the value genrated in [`xrpl.keypairs`](#xrpl-keypairs)):

```py
wallet_from_seed = xrpl.wallet.Wallet(seed)
print(wallet_from_seed)

# print output
seed: sEdTNFV69uSpcHpCppa6VzMvmC68CVY
pub_key: ED46949E414A3D6D758D347BAEC9340DC78F7397FEE893132AAF5D56E4D7DE77B0
priv_key: EDE65EE7882847EF5345A43BFB8E6F5EEC60F45461696C384639B99B26AAA7A5CD
classic_address: rG5ZvYsK5BPi9f1Nb8mhFGDTNMJhEhufn6
```

To create wallet from a Testnet faucet:

```py
TESTNET_WALLET = generate_faucet_wallet(JSON_RPC_CLIENT_TESTNET)
TESTNET_CLASSIC_ACCOUNT = TESTNET_WALLET.classic_address
print("Classic address:\n", TESTNET_CLASSIC_ACCOUNT)

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
CLASSIC_ACCOUNT = keypairs.derive_classic_address(public)
print(f"Here's the public key:\n", public)
print(f"Here's the private key:\n", private +  "\nStore this in a secure place.")
```

**Note:** You can use `xrpl.core.keypairs.sign` to sign transactions but `xrpl-py` also provides explicit methods for safely signing and submitting transactions. See [Transaction Signing](#transaction-signing) and [XRPL Transaction Methods](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html#module-xrpl.transaction) for more information.


### Serialize and sign transactions

To securely submit transactions to the XRP Ledger, you need to first serialize data from JSON and other formats into the [binary format accepted by the XRP Ledger and its core server (`rippled`)](https://xrpl.org/serialization.html#serialization-format), then to [authorize the transaction](https://xrpl.org/transaction-basics.html#authorizing-transactions) by digitally [signing it](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.core.keypairs.html?highlight=sign#xrpl.core.keypairs.sign) with the account's private key. Because this can be error-prone, `xrpl-py` provides methods that simplify the process.


Use the [`xrpl.transaction`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html) module to sign and submit transactions. The module offers three ways to do this:

* [`safe_sign_and_submit_transaction`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html#xrpl.transaction.safe_sign_and_submit_transaction) — Signs a transaction locally, then submits it to the XRP Ledger. This method does not implement [reliable transaction submission](https://xrpl.org/reliable-transaction-submission.html#reliable-transaction-submission) best practices, so only use it for development or testing purposes.

* [`safe_sign_transaction`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html#xrpl.transaction.safe_sign_transaction) — Signs a transaction locally. This method **does  not** submit the transaction to the XRP Ledger.

* [`send_reliable_submission`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.transaction.html#xrpl.transaction.send_reliable_submission) — An implementation of the [reliable transaction submission guidelines](https://xrpl.org/reliable-transaction-submission.html#reliable-transaction-submission), this method signs a transaction locally, submits the transaction to the XRP Ledger, and then verifies that it has been included in a validated ledger (or has failed to do so). Use this method to submit transactions for production purposes.


```py
from xrpl.models.transactions import Payment
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import send_reliable_submission
from xrpl.ledger import get_fee

FEE = get_fee(JSON_RPC_CLIENT)

# prepare the transaction
my_tx_payment = Payment(
    account=TESTNET_CLASSIC_ACCOUNT,
    amount=_AMOUNT,
    destination=TESTNET_DESTINATION_ACCOUNT,
    signing_pub_key=TESTNET_WALLET.pub_key,
    last_ledger_sequence=TESTNET_WALLET.next_sequence_num + 10,
    sequence=TESTNET_WALLET.next_sequence_num,
    fee=FEE,
)
# sign the transaction
my_tx_payment_signed = safe_sign_transaction(my_tx_payment,TESTNET_WALLET)

# submit the transaction
tx_response = send_reliable_submission(my_tx_payment, TESTNET_WALLET, JSON_RPC_CLIENT_TESTNET)
```

### Encode addresses

Use the [`xrpl.core.addresscodec`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.core.addresscodec.html) to encode and decode addresses into the "classic" and X-address formats.

```py
# convert classic address to x-address
>>> from xrpl.core import addresscodec
>>> TESNET_XADDRESS = addresscodec.classic_address_to_xaddress(TESTNET_CLASSIC_ACCOUNT, False, True)
>>> print(TESNET_XADDRESS)
T7CiH636SkvWbU17fKdttaHE97SXQRW1NfMESd67VDcoZTn
```

## Documentation

For complete reference documentation for the library, see [`xrpl-py` docs](https://xrpl-py.readthedocs.io/en/latest/index.html).


## Contributing

If you want to contribute to this project, see [CONTRIBUTING.md].


## License

The `xrpl-py` library is licensed under the ISC License. See [LICENSE] for more information.



[CONTRIBUTING.md]: CONTRIBUTING.md
[LICENSE]: LICENSE
