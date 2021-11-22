"""Utility functions and variables for integration tests."""
import asyncio
import importlib
import inspect
from time import sleep

import xrpl  # noqa: F401 - needed for sync tests
from xrpl.asyncio.clients import AsyncJsonRpcClient, AsyncWebsocketClient
from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction as sign_and_autofill_async,
)
from xrpl.asyncio.transaction import (
    safe_sign_and_submit_transaction as sign_and_submit_async,
)
from xrpl.clients import Client, JsonRpcClient, WebsocketClient
from xrpl.models import Payment, Tx, UnknownRequest
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    safe_sign_and_submit_transaction,
)
from xrpl.wallet import Wallet

JSON_RPC_URL = "http://127.0.0.1:5005"
WEBSOCKET_URL = "ws://127.0.0.1:6006"

JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)
ASYNC_JSON_RPC_CLIENT = AsyncJsonRpcClient(JSON_RPC_URL)

WEBSOCKET_CLIENT = WebsocketClient(WEBSOCKET_URL)
ASYNC_WEBSOCKET_CLIENT = AsyncWebsocketClient(WEBSOCKET_URL)

MASTER_ACCOUNT = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
MASTER_SECRET = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
MASTER_WALLET = Wallet(MASTER_SECRET, 0)
FUNDING_AMOUNT = "400000000"

LEDGER_ACCEPT_REQUEST = UnknownRequest(method="ledger_accept")


async def fund_wallet(client: AsyncClient, wallet: Wallet) -> None:
    payment = Payment(
        account=MASTER_ACCOUNT,
        destination=wallet.classic_address,
        amount=FUNDING_AMOUNT,
    )
    await sign_and_submit_async(payment, MASTER_WALLET, client, check_fee=True)
    await client.request(LEDGER_ACCEPT_REQUEST)


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
    client.request(LEDGER_ACCEPT_REQUEST)
    return client.request(Tx(transaction=signed_tx.get_hash()))


async def sign_and_reliable_submission_async(
    transaction: Transaction, wallet: Wallet, use_json_client: bool = True
) -> Response:
    client = _choose_client_async(use_json_client)
    signed_tx = await sign_and_autofill_async(transaction, wallet, client)
    await client.request(LEDGER_ACCEPT_REQUEST)
    return await client.request(Tx(transaction=signed_tx.get_hash()))


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


def test_async_and_sync(
    original_globals, modules=None, websockets_only=False, num_retries=1
):
    def decorator(test_function):
        lines = _get_non_decorator_code(test_function)
        sync_code = (
            "".join(lines)
            .replace("async def", "def")  # convert method from async to sync
            .replace("async for", "for")  # convert for from async to sync
            .replace("async with", "with")  # convert with from async to sync
            .replace("await ", "")  # replace function calls
            .replace("_async(", "(")  # change methods
            .replace("\n    ", "\n")  # remove indenting (syntax error otherwise)
            .replace("    def", "def")  # remove more indenting
        )
        # add an actual call to the function
        first_line = lines[0]
        sync_code += first_line.replace("    async def ", "").replace(":", "")

        sync_modules_to_import = {}
        if modules is not None:
            for module_str in modules:
                function = module_str.split(".")[-1]
                location = module_str[: -1 * len(function) - 1]
                module = getattr(importlib.import_module(location), function)
                sync_modules_to_import[function] = module

        all_modules = {**original_globals, **globals(), **sync_modules_to_import}
        # NOTE: passing `globals()` into `exec` is really bad practice and not safe at
        # all, but in this case it's fine because it's only running test code

        def _run_sync_test(self, client):
            for i in range(num_retries):
                try:
                    exec(
                        sync_code,
                        all_modules,
                        {"self": self, "client": client},
                    )
                    break
                except Exception as e:
                    if i == num_retries - 1:
                        print(sync_code)  # for debugging, since there's no codefile
                        raise e
                    sleep(2)

        async def _run_async_test(self, client):
            if isinstance(client, AsyncWebsocketClient):
                await client.open()
                # this is happening with each test because IsolatedAsyncioTestCase is
                # setting up a loop for each test cases, so this is the best way to do
                # this
                # happening in `IntegrationTestCase` for the sync client for the sake
                # of efficiency
            for i in range(num_retries):
                try:
                    await test_function(self, client)
                    break
                except Exception as e:
                    if i == num_retries - 1:
                        raise e
                    await asyncio.sleep(2)

            if isinstance(client, AsyncWebsocketClient):
                await client.close()

        def modified_test(self):
            if not websockets_only:
                with self.subTest(version="async", client="json"):
                    asyncio.run(_run_async_test(self, ASYNC_JSON_RPC_CLIENT))
                with self.subTest(version="sync", client="json"):
                    _run_sync_test(self, JSON_RPC_CLIENT)
            with self.subTest(version="async", client="websocket"):
                asyncio.run(_run_async_test(self, ASYNC_WEBSOCKET_CLIENT))
            with self.subTest(version="sync", client="websocket"):
                _run_sync_test(self, WEBSOCKET_CLIENT)

        return modified_test

    return decorator


def _get_non_decorator_code(function):
    code_lines = inspect.getsourcelines(function)[0]
    line = 0
    while line < len(code_lines):
        if "def " in code_lines[line]:
            return code_lines[line:]
        line += 1
