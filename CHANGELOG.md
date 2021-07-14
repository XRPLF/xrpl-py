# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [[Unreleased]]
### Fixed
- Improved documentation on using websocket clients.
- Fixes an issue sending NoRippleCheck requests

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
