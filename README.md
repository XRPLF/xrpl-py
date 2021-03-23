# xrpl-py

A pure Python implementation for interacting with the XRP Ledger, the `xrpl-py` library simplifies the hardest parts of XRP Ledger interaction, like serialization and transaction signing, by providing native Python methods and models for [XRP Ledger](https://xrpl.org/ledger-data-formats.html) and core server [API](https://xrpl.org/api-conventions.html) ([`rippled`](https://github.com/ripple/rippled)) objects.



```py
>>> import xrpl
# create wallet on the testnet
# note that this is split into two steps
# in most cases
>>> from xrpl.clients.json_rpc_client import JsonRpcClient
>>> JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)
>>> wallet = generate_faucet_wallet(JSON_RPC_CLIENT).classic_address
>>> print(wallet)
rQhi8kAuYqHFD28MMGLKMXKnWfeDk2KUjt
# look up account info
>>> from xrpl.models.requests.account_info import AccountInfo
>>> acct_info = AccountInfo(      ...         account=wallet,
...         ledger_index="current",
...         queue=True,
...         strict=True,
...     )
>>> response = JSON_RPC_CLIENT.request(acct_info)
>>> result = response.result
>>> print(json.dumps(result["account_data"], indent=4, sort_keys=True))
# convert classic address to x-address
>>> from xrpl.core.addresscodec.main import classic_address_to_xaddress
>>> xaddress = addresscodec.classic_address_to_xaddress(wallet2_address, True, True)
>>> print(xaddress)
TVegAuMDRSKyAQ7Jx16NtXjhUfEqsQk22EW8CWGzTNrLDgN
# prepare and submit transaction
>>> _FEE = "10"
>>> SET_FLAG = 8
>>> account_set = AccountSet(
...         account=TESTNET_CLASSIC_ACCOUNT,
...         fee=_FEE,
...         sequence=TESTNET_WALLET.next_sequence_num,
...         set_flag=SET_FLAG,
...     )
>>> print(account_set)
>>> response = safe_sign_and_submit_transaction(account_set, TESTNET_WALLET, JSON_RPC_CLIENT_TESTNET)
>>> print("response.status: ", response.status)
response.status:  ResponseStatus.SUCCESS
```


[![Downloads](https://pepy.tech/badge/xrpl-py/month)](https://pepy.tech/project/xrpl-py/month)
[![Contributors](https://img.shields.io/github/contributors/xpring-eng/xrpl-py.svg)](https://github.com/xpring-eng/xrpl-py/graphs/contributors)


## Installation and supported versions

The `xrpl-py` library is available on [PyPI](https://pypi.org/). Install with `pip`:


```
pip3 install xrpl-py
```

The library supports [Python 3.5](https://www.python.org/downloads/) and later.

[![Supported Versions](https://img.shields.io/pypi/pyversions/xrpl-py.svg)](https://pypi.org/project/xrpl-py)


## Features

Use the `xrpl-py` to build Python applications. The library helps with all aspects of interacting with the XRP Ledger, including:

* Key and wallet management
* Serialization
  * method1
* Transaction Signing


## Usage

The following sections describe some of the most commonly used modules in the `xrpl-py` library, including examples.

TODO: Add link to hosted reference docs.
For complete reference documentation, see []()

### Manage keys and wallets

The `xrpl.keypairs` module provides methods for generating seeds, deriving and validating keypairs.

You can use `xrpl.core.keypairs.sign` to sign transactions but `xrpl-py` also provides explicit methods for signing and submitting transactions. See [Transaction Signing](#transaction-signing) for more information.

#### `xrpl.keypairs`


Here's an example of how to generate a `seed` value and derive an [XRP Ledger "classic" address](https://xrpl.org/cryptographic-keys.html#account-id-and-address).


```py
def generate_keys():
    seed = keypairs.generate_seed()
    public, private = keypairs.derive_keypair(seed)
    CLASSIC_ACCOUNT = keypairs.derive_classic_address(public)
    print(f"Here's the public key:\n", public)
    print(f"Here's the private key:\n", private +  "\nStore this in a secure place.")
```



#### `xrpl.wallet`

The `xrpl.wallet` module provides methods to create a wallet from a given seed or or via a [Testnet faucet](https://xrpl.org/xrp-testnet-faucet.html).

To create a wallet from a seed (in this case, the value genrated in [`xrpl.keypairs`](#xrpl-keypairs)):

```py
def create_wallet_from_seed():
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
def create_wallet_from_faucet():
    TESTNET_WALLET = generate_faucet_wallet(JSON_RPC_CLIENT_TESTNET)
    wallet_classic_address = TESTNET_WALLET.classic_address
    print("Classic address:\n", wallet_classic_address)

# print output
Classic address:

 rEQB2hhp3rg7sHj6L8YyR4GG47Cb7pfcuw
```

### Serialization

To securely sign the contents of transactions submitted to the XRP Ledger, you need to serialize data from JSON and other formats into the [binary format accepted by the XRP Ledger and its core server (`rippled`)](https://xrpl.org/serialization.html#serialization-format).


```py
def prepare_tx_current():
    my_tx_current = Payment(
        account=TESTNET_CLASSIC_ACCOUNT,
        amount=_AMOUNT,
        destination=TESTNET_DESTINATION_ACCOUNT,
        memos=_MEMO,
        transaction_type=TransactionType.PAYMENT,
    )
    TESTNET_WALLET.next_sequence_num = get_next_valid_seq_number(TESTNET_CLASSIC_ACCOUNT, JSON_RPC_CLIENT_TESTNET)
```

TODO: add more examples


### Transaction Signing

TODO: add description and examples


## Documentation

In progress, will be linked/discussed here.

## Contributing

If to contribute to this project in [CONTRIBUTING.md].

[CONTRIBUTING.md]: CONTRIBUTING.md

## License

TODO: figure out license

????
