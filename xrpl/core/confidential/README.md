# Confidential Multi-Purpose Token (MPT) Support

This module provides Python bindings for confidential MPT operations using the mpt-crypto C library.

## Overview

The confidential MPT feature uses C libraries built from the [mpt-crypto](https://github.com/XRPLF/mpt-crypto) repository:

- **Static libraries**: `libmpt-crypto.a`, `libsecp256k1.a` (built by CI, included in wheels)
- **C header files**: `secp256k1.h` (in git), `secp256k1_mpt.h` (downloaded during build)
- **Python bindings**: Built using CFFI

This approach uses the same cryptographic library that `rippled` uses internally, ensuring perfect compatibility.

## Installation

Confidential MPT is an **optional feature**. There are different setup paths for end users vs. contributors.

### For End Users (Recommended)

Install xrpl-py with pre-built binaries from PyPI:

```bash
pip install xrpl-py[confidential]
```

The wheel includes all necessary compiled binaries. No build step required!

### For Contributors/Developers

If you're developing xrpl-py locally, you need to set up the MPT crypto binaries:

#### Option 1: Download from CI (Recommended)

```bash
# Download pre-built binaries from the latest CI run
./xrpl/core/confidential/setup_mpt_crypto.sh download

# Build the Python extension
poetry run python xrpl/core/confidential/build_mpt_crypto.py
```

**Requirements**: GitHub CLI (`gh`) installed and authenticated

#### Option 2: Build Locally

```bash
# Build binaries from source
./xrpl/core/confidential/setup_mpt_crypto.sh build

# Build the Python extension
poetry run python xrpl/core/confidential/build_mpt_crypto.py
```

**Requirements**:

- **macOS**: Xcode Command Line Tools, OpenSSL (`brew install openssl`), CMake, Conan
- **Linux**: build-essential, libssl-dev, CMake, Conan
- **Windows**: Use Option 1 (download from CI)

#### Install Dependencies

```bash
poetry install --extras confidential
```

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
├── setup.py                     # Setup script
├── build_mpt_crypto.py          # C extension build script
├── tests/                       # Unit tests
│   ├── test_encryption.py
│   └── test_proofs.py
├── examples/                    # Example scripts
│   ├── submit_confidential_tx.py
│   └── utils.py
├── include/                     # C header files
│   ├── secp256k1.h              # In git
│   └── secp256k1_mpt.h          # Not in git (downloaded by setup)
├── libs/                        # Not in git (created by setup script)
│   ├── darwin/                  # macOS libraries
│   ├── linux/                   # Linux libraries
│   └── win32/                   # Windows libraries
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

## Binary Distribution

### For End Users

Pre-built binaries are included in PyPI wheels for all supported platforms:

- **macOS**: Universal binary (x86_64 + ARM64)
- **Linux**: x86_64
- **Windows**: x86_64

When you `pip install xrpl-py[confidential]`, you get a wheel with all binaries included.

### For Contributors

Binaries are **not stored in git** to keep the repository clean. Instead:

1. **CI builds binaries** for all platforms via `.github/workflows/build_mpt_crypto_libs.yml`
2. **Developers download** from CI artifacts or build locally using `xrpl/core/confidential/setup_mpt_crypto.sh`
3. **Wheels include binaries** built by CI during the release process

### Directory Structure (Local Development)

After running the setup script, you'll have:

```
xrpl/core/confidential/
├── libs/                    # Not in git, created by setup script
│   ├── darwin/              # macOS (universal: x86_64 and arm64)
│   │   ├── libmpt-crypto.a
│   │   └── libsecp256k1.a
│   ├── linux/               # Linux (x86_64)
│   │   ├── libmpt-crypto.a
│   │   └── libsecp256k1.a
│   └── win32/               # Windows (x86_64)
│       ├── mpt-crypto.lib
│       ├── secp256k1.lib
│       ├── crypto.lib       # OpenSSL
│       └── zlib.lib
├── include/
│   ├── secp256k1.h          # In git
│   └── secp256k1_mpt.h      # Not in git, downloaded by setup script
└── _mpt_crypto*.so          # Not in git, built by build_mpt_crypto.py
```

### Building Libraries (For CI/Maintainers)

The GitHub Actions workflow `.github/workflows/build_mpt_crypto_libs.yml` handles building libraries for all platforms. The process:

1. **Clone mpt-crypto** from GitHub
2. **Install dependencies** via Conan (secp256k1, OpenSSL, zlib)
3. **Build static libraries** with platform-specific flags:
   - macOS/Linux: `-DCMAKE_POSITION_INDEPENDENT_CODE=ON` (required for Python extensions)
   - Windows: `/WHOLEARCHIVE` linker flags for proper symbol resolution
4. **Upload artifacts** for use by test jobs and wheel building

See the workflow file for detailed build commands.

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
