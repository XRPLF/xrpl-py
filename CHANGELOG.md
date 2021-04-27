# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Pseudo-transaction models.
- Instance method in `Transaction` objects to calculate their hashes locally
- Option for `Transaction.flags` to be a `List` of `int`s instead of just an `int`
- Optional parameters for `get_transaction_from_hash`: `binary`, `min_ledger` and `max_ledger`
- Enum for `PaymentChannelClaim` flags
- Async version of reliable submission
- Optional parameter to check if the `Transaction` fee is not too high before signing it

### Fixed
- Issue with calculating IOU precision

## [1.0.0] - 2021-03-31
### Added
- Initial release! Please open up an issue in our repo if you have any
  feedback or issues to report.
