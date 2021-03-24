"""Utility functions and variables for integration tests."""

from xrpl.clients import Client, JsonRpcClient
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import safe_sign_and_submit_transaction
from xrpl.wallet import Wallet

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)


def submit_transaction(
    transaction: Transaction, wallet: Wallet, client: Client = JSON_RPC_CLIENT
) -> Response:
    """Signs and submits a transaction to the XRPL."""
    return safe_sign_and_submit_transaction(transaction, wallet, client)
