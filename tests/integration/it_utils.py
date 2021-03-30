"""Utility functions and variables for integration tests."""

from xrpl.clients import JsonRpcClient
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    safe_sign_and_submit_transaction,
    send_reliable_submission,
)
from xrpl.wallet import Wallet

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)


def submit_transaction(transaction: Transaction, wallet: Wallet) -> Response:
    """Signs and submits a transaction to the XRPL."""
    return safe_sign_and_submit_transaction(transaction, wallet, JSON_RPC_CLIENT)


def sign_and_reliable_submission(transaction: Transaction, wallet: Wallet) -> Response:
    signed_tx = safe_sign_and_autofill_transaction(transaction, wallet, JSON_RPC_CLIENT)
    return send_reliable_submission(signed_tx, JSON_RPC_CLIENT)
