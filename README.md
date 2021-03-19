# xrpl-py

A pure Python implementation for interacting with the XRP Ledger. The `xrpl-py` library simplifies the hardest parts of XRP Ledger interaction, like serialization and transaction signing, by providing native Python models for [XRP Ledger](https://xrpl.org/ledger-data-formats.html) and core server [API](https://xrpl.org/api-conventions.html) ([`rippled`](https://github.com/ripple/rippled))  objects.



```py
>>> import xrpl
# generate seed value
>>> from xrpl.core import keypairs
>>> keypairs.generate_seed()
'sEd7rnSJRTCDDtEzwnLvn1mcFYudFMR'
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
>>> response = safe_sign_and_submit_transaction(account_set, TESTNET_WALLET, JSON_RPC_CLIENT_TESTNET)
>>> print(account_set)
>>> response = safe_sign_and_submit_transaction(account_set, TESTNET_WALLET, JSON_RPC_CLIENT_TESTNET)
>>> print("response.status: ", response.status)
response.status:  ResponseStatus.SUCCESS
```


[![Downloads](https://pepy.tech/badge/xrpl-py/month)](https://pepy.tech/project/xrpl-py/month)
[![Supported Versions](https://img.shields.io/pypi/pyversions/xrpl-py.svg)](https://pypi.org/project/xrpl-py)
[![Contributors](https://img.shields.io/github/contributors/xpring-eng/xrpl-py.svg)](https://github.com/xpring-eng/xrpl-py/graphs/contributors)


## Installation

The `xrpl-py` library is available on [PyPI](https://pypi.org/). Install with `pip`:


```
pip3 install xrpl-py
```

The library supports [Python 3.5](https://www.python.org/downloads/) and later.


## Features

TBD

# Usage

TBD

# Documentation

In progress, will be linked/discussed here.

# Contributing

We have collected notes on how to contribute to this project in [CONTRIBUTING.md].

[CONTRIBUTING.md]: CONTRIBUTING.md

# License

????
