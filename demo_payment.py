#!/usr/bin/env python3
"""
xrpl-py Payment Flow Demo
=========================
Demonstrates the three-step SDK pattern for sending XRP:

  Step 1  Define the Transaction  — Payment object, validated before you sign
  Step 2  Sign with Your Key      — seed never leaves your machine
  Step 3  Submit and Wait         — tesSUCCESS + permanent hash in ~3–5 s

Run with:
    cd xrpl-py
    pip install -e .
    python demo_payment.py
"""

# ──────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────────────────────────────
import json

from xrpl.clients import JsonRpcClient
from xrpl.models import Payment
from xrpl.transaction import autofill, sign, submit_and_wait
from xrpl.wallet import Wallet, generate_faucet_wallet

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
NETWORK_URL = "https://s.devnet.rippletest.net:51234/"
EXPLORER_BASE = "https://devnet.xrpl.org"
FAUCET_HOST = None  # None → auto-detect from NETWORK_URL

# ──────────────────────────────────────────────────────────────────────────────
# DISPLAY HELPERS  (same style as demo_xls65_66.py)
# ──────────────────────────────────────────────────────────────────────────────
def banner(title: str) -> None:
    width = 72
    print(f"\n{'━' * width}")
    print(f"  {title}")
    print(f"{'━' * width}")


def step(number: int, label: str) -> None:
    print(f"\n  ▶  Step {number} — {label}")


def print_tx(label: str, response) -> None:
    tx_hash = (
        response.result.get("hash")
        or response.result.get("tx_json", {}).get("hash", "N/A")
    )
    status = response.result.get("meta", {}).get("TransactionResult", "?")
    print(f"    ✅  {label}")
    print(f"        Status  : {status}")
    print(f"        Tx Hash : {tx_hash}")
    print(f"        Explorer: {EXPLORER_BASE}/transactions/{tx_hash}")


def sdk_contrast(label: str, raw: dict, sdk_code: str) -> None:
    print(f"\n  {'─' * 68}")
    print(f"  ✨  SDK MAGIC — {label}")
    print(f"  {'─' * 68}")
    print("  ❌  WITHOUT xrpl-py  (raw JSON crafted + maintained by hand):")
    for line in json.dumps(raw, indent=4).splitlines():
        print(f"      {line}")
    print("\n  ✅  WITH xrpl-py  (type-safe · validated · auto-filled):")
    for line in sdk_code.strip().splitlines():
        print(f"      {line}")
    print(f"  {'─' * 68}\n")


def fund(client: JsonRpcClient, label: str) -> Wallet:
    print(f"\n  ▶  Funding wallet: {label}")
    wallet = generate_faucet_wallet(client, debug=False, faucet_host=FAUCET_HOST)
    print(f"     Address : {wallet.address}")
    return wallet


# ──────────────────────────────────────────────────────────────────────────────
# DEMO
# ──────────────────────────────────────────────────────────────────────────────
def demo_payment(client: JsonRpcClient) -> None:
    banner("xrpl-py · Payment Flow  —  3-Step Pattern")

    sender    = fund(client, "Sender")
    receiver  = fund(client, "Receiver")

    AMOUNT_DROPS = "1000000"   # 1 XRP

    # ── SDK contrast ──────────────────────────────────────────────────────────
    sdk_contrast(
        "Payment — send XRP",
        raw={
            "TransactionType": "Payment",
            "Account": sender.address,
            "Destination": receiver.address,
            "Amount": AMOUNT_DROPS,
            "Fee": "12",
            "Sequence": "<account_info lookup>",
            "LastLedgerSequence": "<ledger + 4 lookup>",
        },
        sdk_code="""\
Payment(
    account=sender.address,
    destination=receiver.address,
    amount="1000000",    # 1 XRP in drops — XRP() not needed for simple send
    # Fee / Sequence / LastLedgerSequence → autofill() fills these in
)""",
    )

    # ── Step 1: Define ────────────────────────────────────────────────────────
    step(1, "Define the Transaction")
    print(
        "\n"
        "    ┌─ What the SDK validates for you ───────────────────────────────┐\n"
        "    │  • account / destination are valid XRPL base58 addresses       │\n"
        "    │  • amount is a string of drops (XRP) or IssuedCurrencyAmount   │\n"
        "    │  • no unknown fields — typos raise an error before you sign    │\n"
        "    └────────────────────────────────────────────────────────────────┘\n"
    )

    payment = Payment(
        account=sender.address,
        destination=receiver.address,
        amount=AMOUNT_DROPS,
    )
    print(f"     Payment object  : {payment.__class__.__name__}")
    print(f"     account         : {payment.account}")
    print(f"     destination     : {payment.destination}")
    print(f"     amount          : {payment.amount} drops  ({int(payment.amount) / 1_000_000} XRP)")
    print(f"     Fee             : {payment.fee}   ← not set yet")
    print(f"     Sequence        : {payment.sequence}   ← not set yet")

    # autofill — show what gets added
    autofilled = autofill(payment, client)
    print(
        "\n"
        f"     After autofill():\n"
        f"       Fee                  : {autofilled.fee} drops\n"
        f"       Sequence             : {autofilled.sequence}\n"
        f"       LastLedgerSequence   : {autofilled.last_ledger_sequence}"
    )

    # ── Step 2: Sign ──────────────────────────────────────────────────────────
    step(2, "Sign with Your Private Key")
    print(
        "\n"
        "    ┌─ What signing does ────────────────────────────────────────────┐\n"
        "    │  sign(tx, wallet) — your seed / private key NEVER leaves       │\n"
        "    │  this machine. The SDK encodes the tx to canonical bytes,      │\n"
        "    │  signs with Ed25519 / secp256k1, and returns a hex blob.       │\n"
        "    │  The network only ever sees the signed blob — not your key.    │\n"
        "    └────────────────────────────────────────────────────────────────┘\n"
    )

    signed_tx = sign(autofilled, sender)
    blob_preview = signed_tx.blob()[:64] + "…"
    algo = "Ed25519" if sender.public_key.startswith("ED") else "secp256k1"
    print(f"     Signed blob (first 64 chars): {blob_preview}")
    print(f"     Signing algorithm           : {algo}")

    # ── Step 3: Submit and Wait ───────────────────────────────────────────────
    step(3, "Submit and Wait for Ledger Validation")
    print(
        "\n"
        "    ┌─ What submit_and_wait() does ──────────────────────────────────┐\n"
        "    │  • Submits the signed blob to the network                      │\n"
        "    │  • Polls until the tx appears in a *validated* ledger          │\n"
        "    │  • Returns only when the result is final — no polling needed   │\n"
        "    │  • Typical latency: 3–5 seconds on XRPL                        │\n"
        "    └────────────────────────────────────────────────────────────────┘\n"
    )

    response = submit_and_wait(signed_tx, client)
    print_tx("Payment confirmed", response)
    print(
        f"\n     Sender   : {sender.address}\n"
        f"     Receiver : {receiver.address}\n"
        f"     Amount   : {int(AMOUNT_DROPS) / 1_000_000} XRP  ({AMOUNT_DROPS} drops)"
    )


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print(
        "\n"
        "╔══════════════════════════════════════════════════════════════════════╗\n"
        "║  xrpl-py Demo  ·  Payment Flow  ·  3-Step Pattern                  ║\n"
        "║  Define → Sign → Submit                                             ║\n"
        "╚══════════════════════════════════════════════════════════════════════╝\n"
    )

    client = JsonRpcClient(NETWORK_URL)
    print(f"  Network : {NETWORK_URL}")
    print(f"  Explorer: {EXPLORER_BASE}")

    try:
        demo_payment(client)
    except Exception as exc:
        print(f"\n  ❌  Demo failed: {exc}")
        raise

    banner("Demo Complete 🎉")
    print(
        "  The 3-step pattern works for every XRPL transaction type:\n"
        "    ✓  Step 1 — Construct a typed model     "
        "  (SDK validates fields before you sign)\n"
        "    ✓  Step 2 — sign(tx, wallet)             "
        "  (private key stays local, blob goes to network)\n"
        "    ✓  Step 3 — submit_and_wait()            "
        "  (blocks until validated — tesSUCCESS + permanent hash)\n"
        "\n"
        f"  Browse all transactions at: {EXPLORER_BASE}\n"
    )


if __name__ == "__main__":
    main()
