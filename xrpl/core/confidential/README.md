# Confidential Multi-Purpose Token (MPT) Support

This module provides Python bindings for confidential MPT operations using the mpt-crypto C library.

## Overview

The confidential MPT feature uses pre-compiled C libraries that are **already included** in the repository:

- **Pre-compiled static libraries**: `libmpt-crypto.a`, `libsecp256k1.a` in `libs/darwin/` (macOS) and `libs/linux/` (Linux)
- **C header files**: `secp256k1.h`, `secp256k1_mpt.h` in `include/`
- **Python bindings**: Built using CFFI

This approach uses the same cryptographic library that `rippled` uses internally, ensuring perfect compatibility.

## Installation

Confidential MPT is an **optional feature**. Regular xrpl-py users don't need to set it up.

### Quick Setup

If you want to use confidential MPT features:

```bash
# 1. Install xrpl-py with confidential support
poetry install --extras confidential

# 2. Build the C extension (one-time)
poetry run python -m xrpl.core.confidential.setup
```

### Alternative: Manual Build

You can also build manually:

```bash
# Using Poetry task (recommended)
poetry run poe build_mpt_crypto

# Or directly with Poetry
poetry run python xrpl/core/confidential/build_mpt_crypto.py
```

### Requirements

- **macOS**: Xcode Command Line Tools (`xcode-select --install`), OpenSSL (`brew install openssl`)
- **Linux**: build-essential, libssl-dev (`sudo apt-get install build-essential libssl-dev`)
- **Windows**: Not yet supported (VLA compatibility issues with MSVC)
- **All platforms**: Python 3.9+ with cffi package (installed via `poetry install --extras confidential`)

## Usage

### Basic Example

```python
from xrpl.core.confidential import MPTCrypto
from xrpl.core.confidential.transaction_builders import prepare_confidential_convert
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet

# Initialize
client = JsonRpcClient("http://localhost:5005")
wallet = Wallet.from_seed("sXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
crypto = MPTCrypto()

# Prepare a confidential convert transaction
tx = prepare_confidential_convert(
    client=client,
    wallet=wallet,
    mpt_issuance_id="000004A2A67A324B17A366D8F0D768C32B23180D6A1E54B7",
    amount=1000,
    crypto=crypto
)

# Sign and submit
from xrpl.transaction import sign_and_submit
response = sign_and_submit(tx, client, wallet)
```

### Available Transaction Builders

The `transaction_builders` module provides high-level functions for all confidential MPT operations:

- **`prepare_confidential_convert()`** - Convert public tokens to confidential
- **`prepare_confidential_merge_inbox()`** - Merge inbox to spending balance
- **`prepare_confidential_send()`** - Transfer confidential tokens between holders
- **`prepare_confidential_convert_back()`** - Convert confidential tokens back to public
- **`prepare_confidential_clawback()`** - Clawback confidential tokens (issuer only)

Each function handles all the complexity of:

- Querying ledger state
- Computing context hashes
- Generating zero-knowledge proofs
- Encrypting amounts
- Constructing the transaction

### Low-Level Cryptographic Operations

For advanced use cases, you can use the `MPTCrypto` class directly:

```python
from xrpl.core.confidential import MPTCrypto

crypto = MPTCrypto()

# Generate ElGamal keypair
privkey, pubkey = crypto.generate_keypair()

# Encrypt an amount
c1, c2, blinding = crypto.encrypt(pubkey, amount=1000)

# Decrypt
decrypted_amount = crypto.decrypt(privkey, c1, c2)

# Create Pedersen commitment
commitment = crypto.create_pedersen_commitment(amount=1000, blinding_factor=blinding)

# Generate proofs
schnorr_proof = crypto.generate_pok(privkey, pubkey, context_id)
link_proof = crypto.create_elgamal_pedersen_link_proof(c1, c2, pubkey, commitment, ...)
```

## Module Structure

```
xrpl/core/confidential/
├── __init__.py                  # Public API exports
├── main.py                      # MPTCrypto wrapper class
├── crypto_bindings.py           # Low-level C library bindings (CFFI)
├── keypair.py                   # Keypair generation and Schnorr PoK
├── encryption.py                # ElGamal encryption/decryption
├── commitments.py               # Pedersen commitments and Bulletproofs
├── link_proofs.py               # ElGamal-Pedersen link proofs
├── plaintext_proofs.py          # Equality and same plaintext proofs
├── transaction_builders.py      # High-level transaction preparation
├── context.py                   # Context hash computation
├── utils.py                     # Utility functions
├── test_utils.py                # Test utilities
├── setup.py                     # Setup script
├── build_mpt_crypto.py          # C extension build script
├── tests/                       # Unit tests
│   ├── test_encryption.py
│   └── test_proofs.py
├── examples/                    # Example scripts
│   └── submit_confidential_tx.py
├── include/                     # C header files
│   ├── secp256k1.h
│   └── secp256k1_mpt.h
├── libs/                        # Pre-compiled native libraries
│   ├── darwin/
│   └── linux/
└── README.md                    # This file
```

## Architecture

The module uses a layered architecture:

1. **Native C Libraries** (`libs/`) - Pre-compiled `libmpt-crypto.a` and `libsecp256k1.a`
2. **CFFI Build** (`build_mpt_crypto.py`) - Compiles C extension linking native libraries
3. **C Extension** (`_mpt_crypto.so`) - Generated platform-specific binary (not in git)
4. **Low-level Bindings** (`crypto_bindings.py`) - Imports CFFI `ffi` and `lib` objects
5. **Functional Modules** (`keypair.py`, `encryption.py`, etc.) - Pure functions taking `ctx` parameter
6. **Wrapper Class** (`main.py`) - `MPTCrypto` class that manages context and delegates to functional modules
7. **Public API** (`__init__.py`) - Exports `MPTCrypto` and transaction builders

The compiled `.so` file is platform and Python-version specific, so it must be rebuilt when:

- Switching Python versions
- Moving to a different platform (macOS, Linux, Windows)
- Updating the `mpt-crypto` C library

## Troubleshooting

### Import Error: "Confidential MPT support is not available"

The C extension hasn't been built yet. Run the setup script:

```bash
poetry run python -m xrpl.core.confidential.setup
```

### Build fails with "Pre-compiled libraries not found"

Your platform may not have pre-compiled libraries yet. Currently supported:

- **macOS** (darwin): ✅ Included
- **Linux**: Coming soon
- **Windows**: Coming soon

### Build fails with "cffi not found"

Install cffi:

```bash
poetry install --extras confidential
```

### Wrong Python version

The `.so` file was built for a different Python version. Rebuild:

```bash
poetry run python -m xrpl.core.confidential.setup
```

## Pre-compiled Libraries

### Directory Structure

```
libs/
├── darwin/          # macOS (universal: x86_64 and arm64)
│   ├── libmpt-crypto.a
│   └── libsecp256k1.a
└── linux/           # Linux (x86_64)
    ├── libmpt-crypto.a
    └── libsecp256k1.a
```

### Building Libraries (For Maintainers)

If you need to rebuild the libraries for your platform:

**Prerequisites:**

- CMake 3.15+
- C compiler (gcc, clang)
- OpenSSL development libraries

**Build Steps:**

```bash
# Clone the mpt-crypto repository
git clone <mpt-crypto-repo-url>
cd mpt-crypto

# Build with -fPIC for shared library linking
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release \
         -DSECP256K1_SOURCE_DIR=/path/to/secp256k1 \
         -DBUILD_SHARED_LIBS=OFF \
         -DBUILD_TESTS=OFF \
         -DBUILD_UTILITY=OFF \
         -DCMAKE_POSITION_INDEPENDENT_CODE=ON
make

# Copy the libraries to xrpl-py
cp libmpt-crypto.a /path/to/xrpl-py/xrpl/core/confidential/libs/<platform>/
cp <secp256k1-build-dir>/lib/libsecp256k1.a /path/to/xrpl-py/xrpl/core/confidential/libs/<platform>/
```

**Important:** Libraries must be compiled with `-fPIC` (Position Independent Code) to be linkable into Python extensions.

## Header Files

The `include/` directory contains C header files required for building:

- `secp256k1.h` - Main secp256k1 library header
- `secp256k1_mpt.h` - MPT-specific extensions

These headers must match the version of the pre-compiled libraries.

## Integration with Poetry

### Optional Dependencies

Confidential MPT support is available as an optional dependency:

```toml
[tool.poetry.dependencies]
cffi = { version = "^1.15.0", optional = true }

[project.optional-dependencies]
confidential = ["cffi>=1.15.0"]

[tool.poetry.extras]
confidential = ["cffi"]
```

### Installation Options

```bash
# With Poetry
poetry install --extras confidential

# With pip
pip install xrpl-py[confidential]
```

### Build Task

A Poetry task is provided to build the C extension:

```bash
poetry run poe build_mpt_crypto
```

## Examples

See the `examples/` directory for complete working examples:

- `submit_confidential_tx.py` - Complete workflow demonstrating all confidential MPT transaction types
