#!/usr/bin/env python3
"""
XLS-66d (Single Asset Vault) + XLS-65d (Lending Protocol) Demo
================================================================
Demonstrates the magic of xrpl-py SDK abstraction for two key XRPL amendments:

  XLS-66d  Single Asset Vault   — on-ledger yield-bearing liquidity vaults
  XLS-65d  Lending Protocol     — permissionless on-ledger secured lending

Each section contrasts "raw JSON" (what you'd write without the SDK) against
the clean, type-safe, auto-filled xrpl-py model to make the abstraction vivid
for a live audience.

Run with:
    cd xrpl-py
    pip install -e .                   # install local xrpl-py build
    python demo_xls65_66.py
"""

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION  ← update these to match your target network
# ──────────────────────────────────────────────────────────────────────────────
NETWORK_URL = "https://s.devnet.rippletest.net:51234/"
EXPLORER_BASE = "https://devnet.xrpl.org"
FAUCET_HOST = None  # None → auto-detect from NETWORK_URL

# ──────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────────────────────────────
import json

from xrpl.clients import JsonRpcClient
from xrpl.models import (
    AccountObjects,
    LoanBrokerSet,
    LoanPay,
    LoanSet,
    VaultCreate,
    VaultDeposit,
    VaultSet,
    VaultWithdraw,
)
from xrpl.models.currencies import XRP
from xrpl.models.requests.account_objects import AccountObjectType
from xrpl.models.transactions.vault_create import WithdrawalPolicy
from xrpl.transaction import (
    autofill_and_sign,
    sign_loan_set_by_counterparty,
    submit_and_wait,
)
from xrpl.utils import str_to_hex
from xrpl.wallet import Wallet, generate_faucet_wallet

# ──────────────────────────────────────────────────────────────────────────────
# DISPLAY HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def banner(title: str) -> None:
    width = 72
    print(f"\n{'━' * width}")
    print(f"  {title}")
    print(f"{'━' * width}")


def step(label: str) -> None:
    print(f"\n  ▶  {label}")


def print_tx(label: str, response) -> None:
    """Print a confirmed transaction with its live Explorer link."""
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
    """Illustrate the abstraction: raw JSON ↔ xrpl-py model."""
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
    """Create and fund a fresh wallet using the network faucet."""
    step(f"Creating & funding wallet: {label}")
    wallet = generate_faucet_wallet(client, debug=False, faucet_host=FAUCET_HOST)
    print(f"     Address : {wallet.address}")
    return wallet

# ──────────────────────────────────────────────────────────────────────────────
# XLS-66d: SINGLE ASSET VAULT DEMO
# ──────────────────────────────────────────────────────────────────────────────
def demo_single_asset_vault(client: JsonRpcClient) -> str:
    """
    Full XLS-66d lifecycle:
        VaultCreate → VaultSet (metadata) → VaultDeposit → VaultWithdraw

    Returns the vault_id so the lending-protocol demo can reuse it.
    """
    banner("XLS-66d · Single Asset Vault  —  Full Lifecycle")

    vault_owner = fund(client, "Vault Owner")
    liquidity_provider = fund(client, "Liquidity Provider (LP)")

    # ── Abstraction contrast ───────────────────────────────────────────────
    sdk_contrast(
        "VaultCreate — open an XRP vault",
        raw={
            "TransactionType": "VaultCreate",
            "Account": vault_owner.address,
            "Asset": {"currency": "XRP"},
            "AssetsMaximum": "10000000",
            "WithdrawalPolicy": 1,
            "Fee": "12",
            "Sequence": "<look up via account_info RPC>",
            "LastLedgerSequence": "<current ledger + 4, via ledger RPC>",
        },
        sdk_code="""\
VaultCreate(
    account=vault_owner.address,
    asset=XRP(),                    # type-safe currency identifier
    assets_maximum="10000000",      # 10 XRP expressed in drops
    withdrawal_policy=WithdrawalPolicy.VAULT_STRATEGY_FIRST_COME_FIRST_SERVE,
    # Fee / Sequence / LastLedgerSequence → auto-filled by submit_and_wait()
)""",
    )

    # Step 1 — Create the vault
    step("VaultCreate")
    response = submit_and_wait(
        VaultCreate(
            account=vault_owner.address,
            asset=XRP(),
            assets_maximum="10000000",
            withdrawal_policy=WithdrawalPolicy.VAULT_STRATEGY_FIRST_COME_FIRST_SERVE,
        ),
        client,
        vault_owner,
    )
    print_tx("Vault created", response)

    # Discover the new vault's ID by querying the ledger
    vault_id = client.request(
        AccountObjects(account=vault_owner.address, type=AccountObjectType.VAULT)
    ).result["account_objects"][0]["index"]
    print(f"     Vault ID: {vault_id}")

    # Step 2 — Annotate the vault with metadata
    step("VaultSet  (attach human-readable metadata)")
    response = submit_and_wait(
        VaultSet(
            account=vault_owner.address,
            vault_id=vault_id,
            data=str_to_hex("XLS-66d Demo Vault | Single Asset Vault on XRPL"),
        ),
        client,
        vault_owner,
    )
    print_tx("Vault metadata updated", response)

    # Step 3 — LP deposits 1 XRP → receives vault shares
    step("VaultDeposit  (LP deposits 1 XRP, receives vault shares in return)")
    response = submit_and_wait(
        VaultDeposit(
            account=liquidity_provider.address,
            vault_id=vault_id,
            amount="1000000",       # 1 XRP in drops
        ),
        client,
        liquidity_provider,
    )
    print_tx("Deposit accepted — LP received vault shares", response)

    # Step 4 — LP redeems shares for XRP
    step("VaultWithdraw  (LP redeems shares, gets XRP back)")
    response = submit_and_wait(
        VaultWithdraw(
            account=liquidity_provider.address,
            vault_id=vault_id,
            amount="500000",        # redeem for 0.5 XRP
        ),
        client,
        liquidity_provider,
    )
    print_tx("Withdrawal complete — XRP returned to LP", response)

    print(f"\n  ✨  XLS-66d demo complete  |  vault_id = {vault_id}")
    return vault_id


# ──────────────────────────────────────────────────────────────────────────────
# XLS-65d: LENDING PROTOCOL DEMO
# ──────────────────────────────────────────────────────────────────────────────
def demo_lending_protocol(client: JsonRpcClient) -> None:
    """
    Full XLS-65d lifecycle:
        VaultCreate → LoanBrokerSet → VaultDeposit (LP) →
        LoanSet (dual-signed) → LoanPay
    """
    banner("XLS-65d · Lending Protocol  —  Full Lifecycle")

    loan_issuer = fund(client, "Loan Issuer  (LoanBroker Owner)")
    depositor   = fund(client, "Depositor    (Liquidity Provider)")
    borrower    = fund(client, "Borrower")

    # Step 1 — Vault that backs the lending protocol
    step("VaultCreate  (XRP vault that will supply lending liquidity)")
    response = submit_and_wait(
        VaultCreate(
            account=loan_issuer.address,
            asset=XRP(),
            assets_maximum="10000000",
            withdrawal_policy=WithdrawalPolicy.VAULT_STRATEGY_FIRST_COME_FIRST_SERVE,
        ),
        client,
        loan_issuer,
    )
    print_tx("Vault created", response)

    vault_id = client.request(
        AccountObjects(account=loan_issuer.address, type=AccountObjectType.VAULT)
    ).result["account_objects"][0]["index"]
    print(f"     Vault ID: {vault_id}")

    # Step 2 — LoanBrokerSet  (abstraction contrast shown here)
    sdk_contrast(
        "LoanBrokerSet — the bridge between vault liquidity and borrowers",
        raw={
            "TransactionType": "LoanBrokerSet",
            "Account": loan_issuer.address,
            "VaultID": vault_id,
            "DebtMaximum": "5000000",
            "ManagementFeeRate": 50,
            "Fee": "12",
            "Sequence": "<account_info lookup>",
            "LastLedgerSequence": "<ledger lookup>",
        },
        sdk_code="""\
LoanBrokerSet(
    account=loan_issuer.address,
    vault_id=vault_id,
    debt_maximum="5000000",    # 5 XRP cap on total outstanding debt
    management_fee_rate=50,    # 5 basis-points management fee
    # Optional: cover_rate_minimum, cover_rate_liquidation …
    # Fee / Sequence / LastLedgerSequence → auto-filled!
)""",
    )

    step("LoanBrokerSet  (register a LoanBroker backed by the vault)")
    response = submit_and_wait(
        LoanBrokerSet(
            account=loan_issuer.address,
            vault_id=vault_id,
            debt_maximum="5000000",
            management_fee_rate=50,
        ),
        client,
        loan_issuer,
    )
    print_tx("LoanBroker registered", response)

    loan_broker_id = client.request(
        AccountObjects(
            account=loan_issuer.address, type=AccountObjectType.LOAN_BROKER
        )
    ).result["account_objects"][0]["index"]
    print(f"     LoanBroker ID: {loan_broker_id}")

    # Step 3 — Depositor provides liquidity to the vault
    step("VaultDeposit  (depositor supplies 2 XRP of lending liquidity)")
    response = submit_and_wait(
        VaultDeposit(
            account=depositor.address,
            vault_id=vault_id,
            amount="2000000",       # 2 XRP in drops
        ),
        client,
        depositor,
    )
    print_tx("Liquidity deposited into vault", response)

    # Step 4 — LoanSet: the crown jewel — dual-party signature
    step("LoanSet  (dual-signed loan agreement — the SDK magic moment)")
    print(
        "\n"
        "    ┌─ SDK MAGIC: Dual-Party Signing ────────────────────────────────┐\n"
        "    │  LoanSet requires TWO cryptographic signatures:                │\n"
        "    │    1. Loan Issuer  — signs the canonical transaction           │\n"
        "    │    2. Borrower     — countersigns the SAME byte sequence       │\n"
        "    │                                                                │\n"
        "    │  xrpl-py exposes one clean call:                               │\n"
        "    │    sign_loan_set_by_counterparty(borrower_wallet, signed_tx)  │\n"
        "    │  It handles encode_for_signing(), key derivation, hex I/O.    │\n"
        "    └────────────────────────────────────────────────────────────────┘\n"
    )

    # Loan Issuer signs first
    loan_set_txn = autofill_and_sign(
        LoanSet(
            account=loan_issuer.address,
            loan_broker_id=loan_broker_id,
            principal_requested="500000",   # 0.5 XRP
            counterparty=borrower.address,
            interest_rate=1000,             # 10 % annualised (in 1/10th bp)
            payment_total=12,               # 12 monthly payments
            payment_interval=86400 * 30,    # ~30 days per payment
            grace_period=86400 * 7,         # 7-day grace period
        ),
        client,
        loan_issuer,
    )
    print("    Loan Issuer signed  ✅")

    # Borrower countersigns — one SDK call abstracts all the complexity
    signed_result = sign_loan_set_by_counterparty(borrower, loan_set_txn)
    print("    Borrower countersigned ✅")

    response = submit_and_wait(signed_result.tx, client)
    print_tx("Loan created — principal disbursed to borrower", response)

    loan_id = client.request(
        AccountObjects(account=borrower.address, type=AccountObjectType.LOAN)
    ).result["account_objects"][0]["index"]
    print(f"     Loan ID: {loan_id}")

    # Step 5 — Borrower repays
    step("LoanPay  (borrower makes an instalment payment)")
    response = submit_and_wait(
        LoanPay(
            account=borrower.address,
            loan_id=loan_id,
            amount="100000",        # 0.1 XRP instalment
        ),
        client,
        borrower,
    )
    print_tx("Loan payment submitted", response)

    print(f"\n  ✨  XLS-65d demo complete  |  loan_id = {loan_id}")


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print(
        "\n"
        "╔══════════════════════════════════════════════════════════════════════╗\n"
        "║  xrpl-py Demo  ·  XLS-66d Single Asset Vault + XLS-65d Lending     ║\n"
        "║  The magic of SDK abstraction on the XRP Ledger                     ║\n"
        "╚══════════════════════════════════════════════════════════════════════╝\n"
    )

    client = JsonRpcClient(NETWORK_URL)
    print(f"  Network : {NETWORK_URL}")
    print(f"  Explorer: {EXPLORER_BASE}")

    try:
        demo_single_asset_vault(client)
        demo_lending_protocol(client)
    except Exception as exc:
        print(f"\n  ❌  Demo failed: {exc}")
        raise

    banner("Demo Complete 🎉")
    print(
        "  Key SDK abstractions demonstrated:\n"
        "    ✓  Type-safe transaction models"
        "       (VaultCreate, LoanBrokerSet, LoanSet …)\n"
        "    ✓  Automatic fee + sequence autofill    "
        "       (submit_and_wait handles it all)\n"
        "    ✓  Reliable submission                  "
        "       (waits for validated-ledger confirmation)\n"
        "    ✓  Dual-party LoanSet signing            "
        "       (sign_loan_set_by_counterparty)\n"
        "    ✓  On-chain object discovery             "
        "       (AccountObjects RPC → vault_id / loan_id)\n"
        "\n"
        f"  Browse all transactions at: {EXPLORER_BASE}\n"
    )


if __name__ == "__main__":
    main()
