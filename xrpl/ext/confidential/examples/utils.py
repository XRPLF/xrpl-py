"""
Test utilities for confidential MPT transactions.

This module provides helper functions for testing confidential MPT transactions,
including account funding, transaction validation, and output formatting.
"""

import json
import sys
from typing import Any

from xrpl.clients import Client
from xrpl.models.requests import AccountObjects, GenericRequest
from xrpl.models.requests.account_objects import AccountObjectType
from xrpl.models.transactions import Payment
from xrpl.transaction import sign_and_submit
from xrpl.wallet import Wallet

# Constants
LEDGER_ACCEPT_REQUEST = GenericRequest(method="ledger_accept")


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_tx_response(response: Any, title: str = "Transaction Response") -> None:
    """Print transaction response in formatted JSON."""
    print(f"\n{title}:")
    print(
        json.dumps(
            response.to_dict() if hasattr(response, "to_dict") else response, indent=2
        )
    )


def check_tx_success(response: Any, tx_name: str) -> None:
    """Check if transaction was successful, exit if not."""
    engine_result = response.result.get("engine_result", "")
    if engine_result != "tesSUCCESS":
        print(f"\nERROR: {tx_name} failed with result: {engine_result}")
        print_tx_response(response, f"{tx_name} Failed")
        sys.exit(1)
    print(f"{tx_name} successful")


def fund_account(
    client: Client, address: str, funder_wallet: Wallet, funding_amount: str
) -> None:
    """Fund an account from the funder wallet."""
    print(f"Funding account {address}...")

    payment = Payment(
        account=funder_wallet.address, destination=address, amount=funding_amount
    )
    response = sign_and_submit(payment, client, funder_wallet)
    check_tx_success(response, "Payment")

    # Accept the ledger in standalone mode
    client.request(LEDGER_ACCEPT_REQUEST)

    print(f"Funded {address}")


def get_mpt_issuance_id(client: Client, issuer_address: str) -> str:
    """Get the MPT issuance ID for an issuer."""
    account_objects = client.request(
        AccountObjects(
            account=issuer_address, type=AccountObjectType.MPT_ISSUANCE, limit=10
        )
    )

    if not account_objects.result.get("account_objects"):
        print("ERROR: No MPT issuances found")
        sys.exit(1)

    mpt_issuance = account_objects.result["account_objects"][0]
    return mpt_issuance["mpt_issuance_id"]
