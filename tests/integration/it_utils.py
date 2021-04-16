"""Utility functions and variables for integration tests."""

from xrpl.clients import Client, JsonRpcClient
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    safe_sign_and_submit_transaction,
    send_reliable_submission,
)
from xrpl.wallet import Wallet

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)


def submit_transaction(
    transaction: Transaction,
    wallet: Wallet,
    client: Client = JSON_RPC_CLIENT,
    check_fee: bool = True,
) -> Response:
    """Signs and submits a transaction to the XRPL."""
    if check_fee is False:
        return safe_sign_and_submit_transaction(
            transaction, wallet, client, True, check_fee
        )
    return safe_sign_and_submit_transaction(transaction, wallet, client)


def sign_and_reliable_submission(
    transaction: Transaction, wallet: Wallet, client=JSON_RPC_CLIENT
) -> Response:
    signed_tx = safe_sign_and_autofill_transaction(transaction, wallet, client)
    return send_reliable_submission(signed_tx, client)
