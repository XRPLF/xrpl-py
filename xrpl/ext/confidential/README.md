# Confidential Multi-Purpose Token (MPT) Support — XLS-0096

Python bindings for confidential MPT operations, backed by the
[mpt-crypto](https://github.com/XRPLF/mpt-crypto) C library (the same crypto
`rippled` uses, so proofs verify on-ledger).

- **Import path:** `xrpl.ext.confidential` (`xrpl.ext` is a PEP 420 namespace
  package — this code ships as the separate `xrpl-py-confidential` distribution,
  so the core `xrpl-py` wheel stays pure-Python).
- **Native pieces:** a thin CFFI extension `_mpt_crypto` that dynamically loads
  `libmpt-crypto.{dylib,so,dll}` (secp256k1 + OpenSSL statically linked inside).
- **Pinned upstream version:** see [`MPT_CRYPTO_VERSION`](./MPT_CRYPTO_VERSION)
  (currently `1.0.1`). The client must build against the same mpt-crypto
  version the target `rippled` was built with.

> **Status:** beta / feature branch. There is no published `xrpl-py-confidential`
> wheel yet, so the only supported path today is the **local build from this
> branch** described below.

## Prerequisites

1. **`gh` CLI** installed and authenticated (used to fetch the native library).
2. **Toolchain** for building the CFFI extension: a C compiler (Xcode CLT on
   macOS, `build-essential` on Linux).

## Quickstart (local build from this branch)

```bash
# 1. Core dependencies
poetry install

# 2. CFFI — required only to BUILD the confidential extension. It is intentionally
#    NOT a core xrpl-py dependency, so install it into the venv explicitly:
poetry run pip install cffi

# 3. Fetch the pinned native shared library into xrpl/ext/confidential/libs/.
#    (Headers are already committed under include/.) Pass the version from
#    xrpl/ext/confidential/MPT_CRYPTO_VERSION (currently 1.0.1):
VERSION=$(grep -E '^MPT_CRYPTO_VERSION=' xrpl/ext/confidential/MPT_CRYPTO_VERSION | cut -d= -f2)
./xrpl/ext/confidential/setup_mpt_crypto.sh download --version "$VERSION"

# 4. Build the CFFI extension (produces _mpt_crypto.<abi>.so in xrpl/ext/confidential/)
poetry run python xrpl/ext/confidential/build_mpt_crypto.py

# 5. Verify it loaded
poetry run python -c "import xrpl.ext.confidential as c; print('available:', c.MPT_CRYPTO_AVAILABLE)"
```

Then run the end-to-end example against your standalone node:

```bash
poetry run python xrpl/ext/confidential/examples/submit_confidential_tx.py
```

It exercises all five transaction types: convert → merge → send → merge →
convert-back → clawback.

## Usage

### High-level transaction builders (recommended)

```python
from xrpl.clients import JsonRpcClient
from xrpl.ext.confidential import MPTCrypto
from xrpl.ext.confidential.transaction_builders import prepare_confidential_convert
from xrpl.transaction import sign_and_submit
from xrpl.wallet import Wallet

client = JsonRpcClient("http://localhost:5005")
wallet = Wallet.from_seed("s...")
crypto = MPTCrypto()

holder_sk, holder_pk = crypto.generate_keypair()
tx = prepare_confidential_convert(
    client=client,
    wallet=wallet,
    mpt_issuance_id="000004A2...",
    amount=1000,
    holder_privkey=holder_sk,
    holder_pubkey=holder_pk,
    issuer_pubkey=issuer_pk,   # the issuance's registered ElGamal key
)
response = sign_and_submit(tx, client, wallet)
```

Builders (each returns a ready-to-sign model with the correct fee already set):

| Function | Transaction |
|---|---|
| `prepare_confidential_convert(client, wallet, ...)` | public → confidential (inbox) |
| `prepare_confidential_merge_inbox(client, wallet, ...)` | inbox → spending balance |
| `prepare_confidential_send(client, sender_wallet, ...)` | confidential transfer |
| `prepare_confidential_convert_back(client, wallet, ...)` | confidential → public |
| `prepare_confidential_clawback(client, issuer_wallet, ...)` | issuer reclaim |

Each handles ledger queries, context-hash computation, ZK-proof generation,
encryption, the confidential fee, and model construction.

### Low-level `MPTCrypto`

```python
crypto = MPTCrypto()
privkey, pubkey = crypto.generate_keypair()
c1, c2, blinding = crypto.encrypt(pubkey, amount=1000)

# NOTE: decrypt brute-forces a discrete log over [range_low, range_high];
# cost is O(range_high - range_low) (~3s per 1,000,000). Bound it tightly —
# e.g. by the issuance's ConfidentialOutstandingAmount, never MaximumAmount.
amount = crypto.decrypt(privkey, c1, c2, range_low=0, range_high=10_000)

commitment = crypto.create_pedersen_commitment(amount=1000, blinding_factor=blinding)
```

## Behaviors worth knowing

- **Confidential fee = `base_fee × 10`.** rippled charges
  `base_fee × (kConfidentialFeeMultiplier + 1)` for ZK-proof verification. The
  builders set this automatically; if you hand-build a confidential transaction
  and let autofill set only the base fee you will get `telINSUF_FEE_P`.
- **`definitions.json` must match the target rippled.** Field codes for the
  confidential fields can shift between rippled builds. If a submit fails with
  `Field '<X>' is required but missing`, regenerate the client definitions from
  the running node's `server_definitions` (see `tools/generate_definitions.py`).
- **Decrypt is O(range)** — see the note above.

## Module structure

```
xrpl/ext/confidential/            # namespace: xrpl.ext.confidential
├── __init__.py                   # public API (MPTCrypto, builders, sizes)
├── main.py                       # MPTCrypto wrapper class
├── crypto_bindings.py            # CFFI ffi/lib loader (graceful if unbuilt)
├── keypair.py                    # keypair + Schnorr PoK
├── encryption.py                 # ElGamal encrypt/decrypt
├── commitments.py                # Pedersen commitments + Bulletproofs
├── plaintext_proofs.py           # clawback (equality) proof
├── context.py                    # context-hash computation
├── transaction_builders.py       # high-level prepare_* functions
├── build_mpt_crypto.py           # CFFI build script (#includes real headers)
├── setup_mpt_crypto.sh           # fetch/build the native libmpt-crypto
├── MPT_CRYPTO_VERSION            # pinned upstream mpt-crypto tag
├── include/                      # vendored headers (committed)
│   ├── secp256k1.h  secp256k1_mpt.h  mpt_protocol.h
│   └── utility/mpt_utility.h
├── libs/                         # native lib — fetched, NOT committed (.gitignore)
└── examples/submit_confidential_tx.py
```

The transaction **models** (`ConfidentialMPT*`) and their `definitions.json`
entries live in core `xrpl-py` (`xrpl/models/transactions/`), so a plain
`xrpl-py` install can construct/sign/serialize/decode these transactions — only
**proof generation** needs this native add-on.

## Packaging & distribution

Native code lives here but ships as the separate **`xrpl-py-confidential`**
distribution, built from [`packaging/confidential/`](../../../packaging/confidential/)
with `cibuildwheel` (see [`SPLIT_DESIGN.md`](../../../packaging/confidential/SPLIT_DESIGN.md)).
Core `xrpl-py` `exclude`s `xrpl/ext/**`, so its wheel stays `py3-none-any`. The
native library is never committed (only the pinned headers are); it is fetched
at dev time by `setup_mpt_crypto.sh` and, in CI, built/fetched per platform.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ImportError: Confidential MPT support is not available` | Extension not built — run the Quickstart (steps 2–4). |
| `ModuleNotFoundError: No module named 'cffi'` | `poetry run pip install cffi` (step 2). |
| `Pre-compiled libraries not found` at build | Native lib not fetched — run `setup_mpt_crypto.sh download` (step 3). |
| Submit fails `Field '...' is required but missing` | Client `definitions.json` out of sync with rippled — regenerate from `server_definitions`. |
| Submit fails `telINSUF_FEE_P` | Confidential fee too low — use the builders (they set `base_fee × 10`). |
| `decrypt` hangs for minutes | `range_high` too large; bound by actual supply, not `MaximumAmount`. |
| `badFeature` for `ConfidentialTransfer` | rippled build lacks the amendment — see Prerequisites. |
