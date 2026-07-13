# Changelog — xrpl-py-confidential

All notable changes to the `xrpl-py-confidential` add-on (`xrpl.ext.confidential`)
are documented in this file.

This package is versioned and released **independently of core `xrpl-py`**: it ships
the optional native cryptography for Confidential MPT (XLS-0096), and its version
tracks the bundled [mpt-crypto](https://github.com/XRPLF/mpt-crypto) release recorded
in `packaging/confidential/version.env`. Changes to the confidential transaction
models, flags, and binary-codec definitions live in the core `xrpl-py` CHANGELOG,
since those ship in core.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [[Unreleased]]

## [0.1.0]

### Added

- Initial release of the native Confidential MPT (XLS-0096) add-on, exposed via
  `xrpl.ext.confidential`:
  - `MPTCrypto` — ElGamal keypair generation, Pedersen commitments, Bulletproofs
    range proofs, Schnorr proofs of knowledge, and discrete-log balance decryption.
  - High-level async/sync transaction builders: `prepare_confidential_convert`,
    `prepare_confidential_convert_back`, `prepare_confidential_send`,
    `prepare_confidential_merge_inbox`, and `prepare_confidential_clawback`
    (each with an `_async` counterpart).
  - CFFI bindings to `mpt-crypto` (with secp256k1 and OpenSSL statically linked),
    built via `build_mpt_crypto.py` / `setup_mpt_crypto.sh`.
- Bundles the pinned `mpt-crypto` release recorded in
  `packaging/confidential/version.env`.
