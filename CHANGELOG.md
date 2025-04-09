# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [[Unreleased]]

### Fixed
- add `MPTAmount` support in `Issue` (rippled internal type)

### Added
- Improved validation for models to also check param types

## [4.1.0] - 2025-2-13

### Added

- Support for `Deep Freeze` (XLS-77d)
- Support for  `PermissionedDomains` (XLS-80)
- Support `AMMClawback` amendment (XLS-73d)
- Support for the `simulate` RPC ([XLS-69](https://github.com/XRPLF/XRPL-Standards/tree/master/XLS-0069d-simulate))

### Fixed
- `Sign`, `SignFor`, and `SignAndSubmit` methods now properly handle WebSocket clients

## [4.0.0] - 2024-12-23

### Added

- Support for the Multi-Purpose Tokens (MPT) amendment (XLS-33)
- Add `include_deleted` to ledger_entry request
- Add support for XLS-70d (Credentials)

### BREAKING CHANGE:

- Remove Python 3.7 support to fix dependency installation and use 3.8 as new default.
- Ensure consistent use of ED25519 as the default cryptographic algorithm in `Wallet.from_secret_numbers` method, aligning with changes made in v2.0.0

### Fixed

- Grab the FeeSettings values from the latest validated ledger. Remove hard-coded reference to 10 drops as the reference transaction cost.

## [3.0.0] - 2024-07-16

### BREAKING CHANGE

- Use rippled API v2 as default in requests

### Added

- Support for the DeliverMax field in Payment transactions
- Support for the `feature` RPC

### Fixed

- Allow empty strings for the purpose of removing fields in DIDSet transaction
- Use `NetworkID` in faucet processing to produce a non-ambiguous URL for faucet hosts.

### Removed

- Remove deprecated `full`, `accounts`, and `type` parameters from ledger request model

## [2.6.0] - 2024-06-03

### Added

- Support for the Price Oracles amendment (XLS-47).
- Add `nfts_by_issuer` clio-only API definition
- Included `ctid` field in the `tx` request.
- `from_xrpl` method accepts input dictionary keys exclusively in the proper XRPL format.
- Support for  DynamicNFT amendment (XLS-46)

### Fixed

- Added support for `XChainModifyBridge` flag maps (fixing an issue with `NFTokenCreateOffer` flag names)
- Fixed `XChainModifyBridge` validation to allow just clearing of `MinAccountCreateAmount`
- Added support for IDE auto-completion of model constructors
- Currency codes with special characters not being allowed by IssuedCurrency objects.
- Construction of Wallet throws an "Invalid Seed" error, if the secret is not decode-able.
- Rectify the incorrect usage of a transaction flag name: Update `TF_NO_DIRECT_RIPPLE` to `TF_NO_RIPPLE_DIRECT`
- Add the missing `AMMDeposit` Flag `TF_TWO_ASSET_IF_EMPTY`

### Removed:

- Remove Hooks faucet since it's now on the Xahau testnet.

## [2.5.0] - 2023-11-30

### Added

- Support for the DID amendment (XLS-40).
- Support for `server_definitions` RPC

### Fixed

- Exported `get_nftoken_id` and `parse_nftoken_id` at the `xrpl.utils` level
- Fixed issue in `get_nftoken_id` where error is opaque when there are no `NFTokenPage`s

### Changed

- Removed sidechain-net1 Devnet faucet support as it has been decommissioned. Users should instead use the bridge between Devnet and sidechain-net2 for testing.
- Removed amm-devnet faucet support as is will soon be decommissioned

## [2.4.0] - 2023-09-27

### Added

- Added new syntax for `SetFee` pseudo transaction sent after the [XRPFees](https://xrpl.org/known-amendments.html#xrpfees) amendment. (Backwards compatible)
- Support for [XLS-38d (XChainBridge)](https://github.com/XRPLF/XRPL-Standards/tree/master/XLS-38d-XChainBridge)

### Fixed

- Update request models related to AMM
- Better error handling for when a `Wallet` is passed into an account or destination field
- Fixed AMMBid fields (BidMin, BidMax) with correct type IssuedCurrencyAmount

## [2.3.0] - 2023-08-24

### Added

- Add AMM support [XLS-30](https://github.com/XRPLF/XRPL-Standards/discussions/78)

## [2.2.0] - 2023-08-07

### Added

- Added new `Clawback` transaction as per [XLS-39](https://github.com/XRPLF/XRPL-Standards/discussions/94)

## [2.1.0] - 2023-07-24

### Fixed

- Replaced alias for `classic_address` with separate property to work around this mypy issue:
  https://github.com/python/mypy/issues/6700

## [2.0.0] - 2023-07-05

### BREAKING CHANGE

- The default signing algorithm in the `Wallet` was changed from secp256k1 to ed25519

### Added:

- Wallet support for regular key compatibility
- Added new ways of wallet generation: `from_seed`, `from_secret`, `from_entropy`, `from_secret_numbers`
- Added `address` alias to `Wallet.classic_address`
  - Replaced `Wallet.classic_address` with `Wallet.address` to avoid confusion. (`classic_address` is the same as your XRPL account `address`, and is only called classic since it's an older standard than `x-address`)
- Added `network_id` to clients in order to use the `Client` with networks beyond mainnet

### Changed:

- Updated params for `Wallet` class constructor
- `Wallet.address` is now readonly
- Removed `sequence` from `Wallet` class
- Core keypairs generate seed must take in hexstring instead of bytestring
- Core keypairs formatting for `ED25519` is now padded with zeros if length of keystring is less than 64
- Removed deprecated request wrappers (the preferred method is to directly do client.request instead)
- `AccountSetFlagInterface` now operates on transaction `tf` flags (as opposed to `asf` flags)
- `sign` is now synchronous instead of async (done by removing the optional `check_fee` param & moving checks up to other functions)
- In order to be internally consistent, all signing/submitting functions will follow the parameter order of `transaction`, `client`, `wallet`, and then other parameters. (This is because `wallet` is optional for `submit_and_wait` and so must come after `client`)
- `XRP.to_amount` now converts from XRP to drops, instead of expecting a drops amount

### Fixed:

- Added a sort of the account IDs in `multisign`, so that the `multisign` always works.
- Add `ledger_hash` and `ledger_index` to `account_nfts`, `nft_buy_offers`, and `nft_sell_offers` requests.
- Add `nft_page` to `ledger_entry` request.

### Removed:

- `send_reliable_submission` has been replaced by `submit_and_wait`
- Longer aliases for signing/submitting functions have been removed. Specifically
  - `submit_transaction` is now `submit`
  - `safe_sign_transaction` is now `sign`
  - `safe_sign_and_submit_transaction` is now `sign_and_submit`
    - The param order for `sign_and_submit` moves `wallet` after `client` to be consistent with `submit_and_wait`
  - `safe_sign_and_autofill_transaction` is now `autofill_and_sign`
    - The param order for `autofill_and_sign` moves `wallet` after `client` to be consistent with `submit_and_wait`
- Removed deprecated request functions which were just wrappers around `Client.request()`. Specifically this includes:
  - `get_account_info`
  - `get_account_transactions`
  - `get_account_payment_transactions`
  - `get_transaction_from_hash`

## [1.9.0] - 2023-06-13

### Added:

- Added `submit_and_wait` to sign (if needed), autofill, submit a transaction and wait for its final outcome
- `submit` and `send_reliable_submission` now accept an optional boolean param `fail_hard` (if `True` halt the submission if it's not immediately validated)
- Added sidechain devnet support to faucet generation
- Added `user_agent` and `usage_context` to `generate_faucet_wallet`

### Changed:

- Allowed keypairs.sign to take a hex string in addition to bytes

### Fixed:

- Refactored `does_account_exist` and `get_balance` to avoid deprecated methods and use `ledger_index` parameter
- Fixed crashes in the `SignerListSet` validation
- Improved error messages in `send_reliable_submission`
- Better error handling in reliable submission

### Removed:

- RPCs and utils related to the old sidechain design

## [1.8.0] - 2023-04-10

### Added:

- Created function alias to `safe_sign_transaction` called `sign` - safe originally used to indicate local offline signing (keys aren't exposed)
- Created function alias to `safe_sign_and_autofill_transaction` called `autofill_and_sign` to reflect order of operations
- Created function alias to `submit_transaction` called `submit`
- Created function alias to `safe_sign_and_submit_transaction` called `sign_and_submit`
- AccountSetFlags for disallowing incoming objects (e.g. `asf_disallow_incoming_trustline`)
- Added `getNFTokenID` to get the NFTokenID after minting a token.
- Added `LedgerEntryType` enum and added `type` field to `Ledger` and `LedgerData` requests
- Added the algorithm used to encode a wallet's seed to the wallet.

### Changed:

- `check_fee` now has a higher limit that is less likely to be hit
- When connected hooks v2 testnet generate_faucet_wallet now defaults to using the faucet instead of requiring specification
- Deprecated `get_account_info`, `get_transaction_from_hash`, `get_account_payment_transactions` for direct requests
- Private function `request_impl` has been renamed to `_request_impl`. Users should always use `request` over `request_impl`.
- Removed nft-devnet faucet support as it has been decommissioned ([Blog Post](https://xrpl.org/blog/2023/nft-devnet-decommission.html))

### Fixed:

- Properly type the instance functions of NestedModel
- Add additional check to `txnNotFound` error from `reliable_submission` due to race condition
- Add `nft_offer` type in `AccountObjects`
- Handle errors better in `send_reliable_submission`
- Made `send_reliable_submission` wait the full duration until `LastLedgerSequence` passes by

## [1.7.0] - 2022-10-12

### Added:

- Support for ExpandedSignerList amendment that expands the maximum signer list to 32 entries
- Function to parse the final account balances from a transaction's metadata
- Function to parse order book changes from a transaction's metadata
- Support for Ed25519 seeds that don't use the `sEd` prefix
- Support for Automated Market Maker (AMM) transactions and requests as defined in XLS-30.
- Add docs to`get_account_transactions` explaining how to allow pagination through all transaction history [#462]
- Common field `ticket_sequence` to Transaction class

### Fixed:

- Typing for factory classmethods on models
- Use properly encoded transactions in `Sign`, `SignFor`, and `SignAndSubmit`
- Fix Sphinx build errors due to incompatible version bumps

## [1.6.0] - 2022-06-02

### Added:

- Support for dynamic fee calculation
- Function to parse account balances from a transaction's metadata
- Better error handling for invalid client URL
- Exported SubscribeBook

### Fixed

- Resolve `txnNotFound` error with `send_reliable_submission` when waiting for a submitted malformed transaction
- Small typing mistake in GenericRequest
- Fix bug in GenericRequest.to_dict()

## [1.5.0] - 2022-04-25

### Added

- Support setting flags with booleans. For each transaction type supporting flags there is a `FlagInterface` to set the flags with booleans.
- `federator_info` RPC support
- Helper method for creating a cross-chain payment to/from a sidechain
- Helper method for parsing an NFTokenID

### Fixed

- Updated NFT names to match new 1.9.0 rippled names
- `xrpl.asyncio.clients` exports (now includes `request_to_websocket`, `websocket_to_response`)
- Adds optional `owner` field to NFTokenBurn
- Allows lower-case currency codes

## [1.4.0] - 2022-02-24

### Added

- Sync and async `generate_faucet_wallet` functions now support a custom
  faucet host

## [1.3.0] - 2021-12-17

### Added

- Support for the [XLS-20 NFT proposal](https://github.com/XRPLF/XRPL-Standards/discussions/46)
- `xrpl.models.amounts.get_amount_value` helper function
- `xrpl.utils.str_to_hex` and `xrpl.utils.hex_to_str` helpers
- `ledger_index` optional param for all the main account methods
- `TicketCreate` transaction model
- `GenericRequest` model for unsupported request types
- Methods to convert between `IssuedCurrency` and `IssuedCurrencyAmount`
- Support for ints and floats in the `IssuedCurrency` and `IssuedCurrencyAmount` models (and ints for `XRP`)
- `max_fee` and `fee_type` optional params for `get_fee`
- `autofill`, a new public method that populates the `fee`, `sequence`, and `last_ledger_sequence` fields of a transaction, based on the current state retrieved from the server the Client is connected to. It also converts all X-Addresses to classic addresses.
- Exports `Transaction`, `Response`, pseudo-transactions at the `xrpl.models` level

### Fixed

- Improves typing of `Response.result`
- Makes the default ledger version for `get_next_valid_seq_number` `current` instead of `validated`
- Stops erroring on non-`tesSUCCESS` responses in reliable transaction submission
- Removes runtime asserts in websocket clients that were used for type checks only
- Adds missing top-level `py.typed` file for exceptions and constants
- Fix issue where unsupported currency codes weren't being correctly processed in the binary codec
- Fixes issue with UNLModify encoding (due to a bug in rippled)
- Makes the account delete fee dynamic, based on the ledger's reserve, instead of hard-coded
- Fee scaling based on load on the ledger
- Fixes potential issue with conflicting Decimal contexts
- Fixes bug where autofilling using an `xAddress` with `None` in the Destination Tag threw a KeyError

## [1.2.0] - 2021-11-09

### Added

- Support for Python 3.10

### Fixed

- Improves documentation on using websocket clients.
- Fixes an issue sending NoRippleCheck requests
- Allows projects that use xrpl-py as a dependency to use typing

## [1.1.1] - 2021-07-02

### Fixed

- Fixes an issue encoding some non-standard currency values
- Corrects installation instructions in documentation

## [1.1.0] - 2021-06-16

### Added

- Option for `Transaction.flags` to be a `List` of `int`s instead of just an `int`
- Instance method in `Transaction` objects to calculate their hashes locally
- Additional reliability to `send_reliable_submission` by getting the hash before submitting
- Pseudo-transaction models
- Optional parameters for `get_transaction_from_hash`: `binary`, `min_ledger` and `max_ledger`
- Enum for `PaymentChannelClaim` flags
- Optional parameter to check if the `Transaction` fee is not too high before signing it
- Additional X-Address support in the binary codec and account sugar
- Method to the `Wallet` class that generates the X-Address for the wallet's account
- Async versions of all high-level functionality within the `xrpl.asyncio` package
- Web socket client under `xrpl.clients.WebsocketClient`
- Async web socket client under `xrpl.asyncio.clients.AsyncWebsocketClient`
- A general `from_dict` method for `Request` models, analogous to `Transaction.from_dict`

### Fixed

- Typos in docs/tests
- Improved readability of the README/documentation
- Expose `xrpl.utils` at the top level
- Expose `xrpl.accounts.get_account_root`
- Issue with calculating IOU precision
- Invalid X-Addresses in the XRPL Binary Codec now error with `XRPLBinaryCodecException` instead of `ValueError`
- Issues with converting certain dictionaries to/from a model using `BaseModel.from_dict`
- Better error message reporting

## [1.0.0] - 2021-03-31

### Added

- Initial release! Please open up an issue in our repo if you have any
  feedback or issues to report.
