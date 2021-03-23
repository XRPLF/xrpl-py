# xrpl-py

A pure Python implementation for interacting with the XRP Ledger, the `xrpl-py` library simplifies the hardest parts of XRP Ledger interaction, like serialization and transaction signing, by providing native Python methods and models for [XRP Ledger](https://xrpl.org/ledger-data-formats.html) and core server [API](https://xrpl.org/api-conventions.html) ([`rippled`](https://github.com/ripple/rippled)) objects.



```py
>>> import xrpl
# create a wallet on the testnet
>>> from xrpl.clients.json_rpc_client import JsonRpcClient
>>> JSON_RPC_URL_TESTNET = "https://s.altnet.rippletest.net:51234/"
>>> JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL_TESTNET)
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
# convert classic address to x-address
>>> from xrpl.core import addresscodec
>>> TESNET_XADDRESS = addresscodec.classic_address_to_xaddress(TESTNET_CLASSIC_ACCOUNT, False, True)
>>> print(TESNET_XADDRESS)
T7CiH636SkvWbU17fKdttaHE97SXQRW1NfMESd67VDcoZTn
# prepare and submit an AccountSet transaction
>>> from xrpl.account import get_next_valid_seq_number
>>> _FEE = "10"
>>> SET_FLAG = 8
>>> TESTNET_WALLET.next_sequence_num = get_next_valid_seq_number(TESTNET_CLASSIC_ACCOUNT, JSON_RPC_CLIENT)
>>> from xrpl.models.transactions import AccountSet, Payment
>>> account_set = AccountSet(
...         account=TESTNET_CLASSIC_ACCOUNT,
...         fee=_FEE,
...         sequence=TESTNET_WALLET.next_sequence_num,
...         set_flag=SET_FLAG,
...     )
>>> print(account_set)
AccountSet(account='ra9cjuPRq7tmR3Uin3y6fUPKLZ317JLvbN', transaction_type=<TransactionType.ACCOUNT_SET: 'AccountSet'>, fee='10', sequence=16007556, account_txn_id=None, flags=0, last_ledger_sequence=None, memos=None, signers=None, source_tag=None, signing_pub_key=None, txn_signature=None, clear_flag=None, domain=None, email_hash=None, message_key=None, set_flag=8, transfer_rate=None, tick_size=None)
>>> response = safe_sign_and_submit_transaction(account_set, TESTNET_WALLET, JSON_RPC_CLIENT)
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

The library supports [Python 3.7](https://www.python.org/downloads/) and later.

[![Supported Versions](https://img.shields.io/pypi/pyversions/xrpl-py.svg)](https://pypi.org/project/xrpl-py)


## Features

Use `xrpl-py` to build Python applications that leverage the [XRP Ledger](https://xrpl.org/). The library helps with all aspects of interacting with the XRP Ledger, including:

* Key and wallet management
* Serialization
* Transaction Signing

`xrpl-py` also provides various other convenience methods, including:

* Network client: See [`xrpl.clients`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.clients.html) for more information.
* Methods for insepcting accounts: See [XRPL Account Methods](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.account.html)

## Usage

The following sections describe some of the most commonly used modules in the `xrpl-py` library and provide sample code.

For complete reference documentation, see the [`xrpl-py` docs](https://xrpl-py.readthedocs.io/en/latest/index.html).

### Manage keys and wallets

The `xrpl.keypairs` module provides methods for generating seeds, deriving, and validating keypairs.


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


Use the [`xrpl.core.keypairs`](https://xrpl-py.readthedocs.io/en/latest/source/xrpl.core.keypairs.html#module-xrpl.core.keypairs) module to generate seeds and derive keypairs and addresses from seeds.

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




### Serialization

To securely sign the contents of transactions submitted to the XRP Ledger, you need to serialize data from JSON and other formats into the [binary format accepted by the XRP Ledger and its core server (`rippled`)](https://xrpl.org/serialization.html#serialization-format).

Use the `xrpl.models.transactions` module to prepare transactions in the formats expected by the XRP Ledger.

```py
from xrpl.models.transactions import AccountSet, Payment
from xrpl.models.transactions.transaction import Transaction, TransactionType, Memo
from xrpl.core.binarycodec import encode_for_signing
my_tx_payment = Payment(
    account=TESTNET_CLASSIC_ACCOUNT,
    amount=_AMOUNT,
    destination=TESTNET_DESTINATION_ACCOUNT,
    memos=_MEMO,
)
print(my_tx_payment)
serialized_tx_payment = encode_for_signing(my_tx_payment)
serialized_tx_payment = encode(my_tx_payment)


# print output
Payment(account='rnCvKZut85Zgvvx3PjALvjQpn25RNTgj9T', transaction_type=<TransactionType.PAYMENT: 'Payment'>, fee=None, sequence=None, account_txn_id=None, flags=0, last_ledger_sequence=None, memos='I sent this with xrpl-py!', signers=None, source_tag=None, signing_pub_key=None, txn_signature=None, amount='20', destination='rBCLR6TTxUf171Dshu92AMbrKLVXLVceRy', destination_tag=None, invoice_id=None, paths=None, send_max=None, deliver_min=None)

my_tx_account_set = AccountSet(
        account=TESTNET_CLASSIC_ACCOUNT,
        fee=_FEE,
        sequence=TESTNET_WALLET.next_sequence_num,
        set_flag=SET_FLAG,
)
print(my_tx_account_set)

# print output
AccountSet(account='rnCvKZut85Zgvvx3PjALvjQpn25RNTgj9T', transaction_type=<TransactionType.ACCOUNT_SET: 'AccountSet'>, fee='10', sequence=16011745, account_txn_id=None, flags=0, last_ledger_sequence=None, memos=None, signers=None, source_tag=None, signing_pub_key=None, txn_signature=None, clear_flag=None, domain=None, email_hash=None, message_key=None, set_flag=8, transfer_rate=None, tick_size=None)
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
