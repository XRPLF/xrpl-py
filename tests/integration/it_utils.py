"""Utility functions and variables for integration tests."""

from xrpl.asyncio.clients import AsyncJsonRpcClient, AsyncWebsocketClient
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction as sign_and_autofill_async,
)
from xrpl.asyncio.transaction import (
    safe_sign_and_submit_transaction as sign_and_submit_async,
)
from xrpl.asyncio.transaction import (
    send_reliable_submission as send_reliable_submission_async,
)
from xrpl.clients import Client, JsonRpcClient, WebsocketClient
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    safe_sign_and_submit_transaction,
    send_reliable_submission,
)
from xrpl.wallet import Wallet

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
WEBSOCKET_URL = "wss://s.altnet.rippletest.net/"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)
ASYNC_JSON_RPC_CLIENT = AsyncJsonRpcClient(JSON_RPC_URL)
WEBSOCKET_CLIENT = WebsocketClient(WEBSOCKET_URL)
ASYNC_WEBSOCKET_CLIENT = AsyncWebsocketClient(WEBSOCKET_URL)

CLIENTS = [
    JSON_RPC_CLIENT,
    ASYNC_JSON_RPC_CLIENT,
    WEBSOCKET_CLIENT,
    ASYNC_WEBSOCKET_CLIENT,
]


def submit_transaction(
    transaction: Transaction,
    wallet: Wallet,
    client: Client = JSON_RPC_CLIENT,
    check_fee: bool = True,
) -> Response:
    """Signs and submits a transaction to the XRPL."""
    return safe_sign_and_submit_transaction(
        transaction, wallet, client, check_fee=check_fee
    )


async def submit_transaction_async(
    transaction: Transaction,
    wallet: Wallet,
    client: Client = ASYNC_JSON_RPC_CLIENT,
    check_fee: bool = True,
) -> Response:
    return await sign_and_submit_async(transaction, wallet, client, check_fee=check_fee)


def sign_and_reliable_submission(
    transaction: Transaction, wallet: Wallet, use_json_client: bool = True
) -> Response:
    client = _choose_client(use_json_client)
    signed_tx = safe_sign_and_autofill_transaction(transaction, wallet, client)
    return send_reliable_submission(signed_tx, client)


async def sign_and_reliable_submission_async(
    transaction: Transaction, wallet: Wallet, use_json_client: bool = True
) -> Response:
    client = _choose_client_async(use_json_client)
    signed_tx = await sign_and_autofill_async(transaction, wallet, client)
    return await send_reliable_submission_async(signed_tx, client)


def _choose_client(use_json_client: bool) -> Client:
    if use_json_client:
        return JSON_RPC_CLIENT
    else:
        return WEBSOCKET_CLIENT


def _choose_client_async(use_json_client: bool) -> Client:
    if use_json_client:
        return ASYNC_JSON_RPC_CLIENT
    else:
        return ASYNC_WEBSOCKET_CLIENT
