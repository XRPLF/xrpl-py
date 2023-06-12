# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [[Unreleased]]
### Added:
- Added `submit_and_wait` to sign (if needed), autofill, submit a transaction and wait for its final outcome
- `submit` and `send_reliable_submission` now accept an optional boolean param `fail_hard` (if `True` halt the submission if it's not immediately validated)
- Added sidechain devnet support to faucet generation

### Changed:
- Allowed keypairs.sign to take a hex string in addition to bytes

### Fixed:
- Refactored `does_account_exist` and `get_balance` to avoid deprecated methods and use `ledger_index` parameter
- Fixed crashes in the SignerListSet validation
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
