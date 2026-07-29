# Reviewing xrpl-py

xrpl-py is the canonical **Python SDK for the XRP Ledger** (`xrpl/`: models, binary codec, keypairs,
address codec, sync + async clients). It is a **financial primitive**: amount, serialization, and
signing bugs corrupt transactions or break consensus compatibility and surface only against a
live network. **rippled is the source of truth** — verify fields, types, and flags against it,
not intuition or a draft spec.

## Amounts & numbers
- A bare `str` in the `Amount` union is XRP in **drops** (integer string; the codec rejects any
  decimal point in XRP/MPT strings — don't suggest accepting them). IOU `value` strings may be
  decimal.
- Amount **encode** (`Amount.from_value`) and drops conversions wrap Decimal math in
  `IOU_`/`DROPS_DECIMAL_CONTEXT`; flag new plain-context Decimals there. Decode (`Amount.to_json`)
  uses the ambient context deliberately — don't flag it.
- Decimal→string on encode paths must force fixed-point (`f"{value:f}"`) and only `rstrip("0")` when
  a `.` is present (a 5.0.0 truncation fix). Flag a new full-value `str(Decimal)` or a `rstrip("0")`
  on an un-split value; a rstrip on an already-separated fractional slice is fine.
- IOU bounds are protocol-fixed (≤16 significant digits, exponent −96…80); underflow **silently
  rounds to zero encoding** (matches rippled). MPT values are unsigned 63-bit integer strings (the
  MSB is spec).
- The model layer is deliberately lenient (`IssuedCurrencyAmount.value` = `str|int|float`);
  validation lives in the codec. DO flag IOU values round-tripped through `float` on encode paths.

## Binary serialization & the Number type
- **Round-trip is the core invariant**: `encode(decode(blob)) == blob`, `decode(encode(json)) ==
  json`. A new/changed `SerializedType` needs both directions in lockstep plus round-trip tests.
- Wire order is **ordinal** (`type_code << 16 | nth`, sorted in `STObject.from_value`); unsorted
  output looks valid but rippled rejects it.
- The `Number` codec deliberately **ports rippled's C++ Number/STNumber** (sentinel zero, string-built
  `to_json`). Don't suggest idiomatic-Python numerics; changes need boundary tests.
- A type named in `definitions.json` needs a `SerializedType` class **imported and in `__all__`** of
  `binarycodec/types/__init__.py`: resolution raises `KeyError` lazily on first field use
  (survives CI that never exercises it).

## Generated code (definitions.json & transaction models)
- `definitions.json` is **machine-generated** from rippled headers (`poe definitions <rippled ref>`;
  `poe generate` also regenerates models). Hand-edits are lost on regen — a hand-edited
  definitions.json is itself the finding. Verify changed mappings against rippled's macros (the
  5.0.0 `sfMutableFlags` mis-mapping).
- In a definitions.json diff, mass **TER-code renumbering is legitimate** (implicit-increment
  derivation; check anchors like `tesSUCCESS = 0`), but unexplained **deletions are the red flag** —
  the generator's regexes silently drop macro lines they fail to parse.
- Transaction models are **generated once, then hand-maintained**: hand-edits survive regen; a bare
  new model needing hand-finishing is normal. A `TRANSACTION_TYPES` addition with **no matching
  model file** usually means the model generator's regex dropped it.

## Transaction models & validation
- Adding a tx type touches **three sites**: model module; `TransactionType` member whose value
  **exactly equals the class name**; import **and** `__all__` entry in `transactions/__init__.py`. A
  missing **import** breaks polymorphic `from_dict` for **every** type (eager `getattr` dispatch); a
  missing `__all__` entry breaks dict-style flag parsing.
- Every model subclass declaring fields needs its **own `@dataclass(frozen=True, kw_only=True)`** —
  not inherited; without it the fields are silently excluded from `__init__`.
- Flags are name-coupled: `{TxType}Flag(int, Enum)` + `{TxType}FlagInterface` (identical member
  names), both in `__all__` — a mismatch makes dict-style flags silently resolve to 0.
- `_get_errors()` overrides must merge `super()._get_errors()`; a fresh dict silently disables all
  inherited validation. Flag-dependent checks belong here via `self.has_flag(...)`.
- `field: T = REQUIRED` (an `object()` sentinel) is the required-field idiom
  (optional = `Optional[T] = None`); `transaction_type: ... = field(..., init=False)` + its
  `to_dict`/`from_dict` special-casing is the dispatch contract. Don't flag either.
- Never default `flags` to 0 — omitted `Flags` vs `Flags: 0` changes the signed bytes.
- Models are **STRICT — the opposite of xrpl.js**: `from_dict` raises on unknown keys (and real
  rippled responses via `from_xrpl`). Don't suggest ignoring them. When rippled adds a field, the
  model update must land with it.

## Cryptography & signing
- Secrets never appear in `__repr__`/`__str__`/exceptions: `_SENSITIVE_FIELDS` + a redacting
  `__repr__` emit `-HIDDEN-`; new sensitive fields extend it. Seed validation re-raises with
  `from None` (base58 errors embed seed bytes) — don't flag that; DO flag new interpolation of
  seeds/keys/entropy into strings.
- Seed-prefix inference is **load-bearing**: `sEd…` → ED25519, else SECP256K1; explicit `algorithm`
  wins. Changing inference or defaults silently derives a **different address from the same seed**.
  Don't suggest an ED25519 default for externally supplied seeds.
- Signing is XRPL-spec: secp256k1 = `sha512_first_half` prehash + RFC-6979 + `canonical=True` low-S
  (flag new signing code missing any); ed25519 signs the raw message — the asymmetry is spec.
- Four prefixes (`STX`/`CLM`/`SMT`/`BCH`) domain-separate single-sign/claim/multisign/Batch
  payloads; multisigning appends the signer AccountID suffix. Wrong/shared prefix or missing suffix
  = signature replay. Outer `SigningPubKey` stays `""` when multisigning; signer arrays sort by
  **decoded AccountID bytes**, not the base58 string; Batch uses `encode_for_signing_batch` only.
- `isSigningField` changes in definitions.json are signature-compatibility breaks; verify against
  rippled.

## Sync/async parity (hand-maintained)
- The async side is the implementation; sync functions in `xrpl/{account,ledger,transaction,wallet}/`
  are verbatim `asyncio.run(...)` delegates with duplicated signatures/docstrings (the parity
  contract). There is **no parity check**: flag edits to one side of a paired function without the
  matching edit — drift fails silently.

## Client & response handling
- Transports never raise on rippled app errors: non-`success` returns `Response(status=ERROR)`;
  callers gate on `is_successful()`. DO flag new helpers reading `response.result` without a
  status check (WS errors put fields at top level).
- The WebSocket `_handler` must **exception-isolate each frame**: one malformed frame must not kill
  the handler task and every pending Future. Its internals (double delivery, fire-and-forget sends,
  wide request IDs) are deliberate — flag removals, not oddity.

## Test conventions (do NOT flag)
- `snoPBrXtMeMyMHUVTgbuqAfg1SUTb` (and its `rHb9…` address) in `tests/integration/` is rippled's
  public standalone-mode genesis account, not a leaked secret.
- `@test_async_and_sync(globals())` **textually rewrites** async test bodies and `exec()`s the sync
  variant — deliberate harness mechanics, not unsafe exec. Check the contract instead: tests are
  `async def test_*(self, client)` on an `IntegrationTestCase` subclass, call helpers by their
  `_async` names, and reuse `reusable_values.py` fixtures.

## Contributor conventions
- Python floor is **3.10** (CI up to 3.14): flag newer-than-3.10 syntax, and `Self`/`TypeVar(default=)`
  imported from `typing` instead of `typing_extensions`. Don't request 3.8/3.9 compatibility.
- `.github/xrpld-image.env` is high-blast-radius CI config: a committed private version redirects
  the **integration-test** workflow (every PR run) and breaks fork-PR CI. Verify it's intentional and reset.
