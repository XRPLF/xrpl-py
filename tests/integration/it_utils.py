"""Utility functions and variables for integration tests."""
import asyncio
import importlib
import inspect
from time import sleep

import xrpl  # noqa: F401 - needed for sync tests
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
DEV_JSON_RPC_URL = "https://s.devnet.rippletest.net:51234"
WEBSOCKET_URL = "wss://s.altnet.rippletest.net/"

JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)
ASYNC_JSON_RPC_CLIENT = AsyncJsonRpcClient(JSON_RPC_URL)
WEBSOCKET_CLIENT = WebsocketClient(WEBSOCKET_URL)
ASYNC_WEBSOCKET_CLIENT = AsyncWebsocketClient(WEBSOCKET_URL)

DEV_JSON_RPC_CLIENT = JsonRpcClient(DEV_JSON_RPC_URL)
DEV_ASYNC_JSON_RPC_CLIENT = AsyncJsonRpcClient(DEV_JSON_RPC_URL)


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


def test_async_and_sync(original_globals, modules=None, dev=False):
    def decorator(test_function):
        lines = _get_non_decorator_code(test_function)
        sync_code = (
            "".join(lines)
            .replace("async def", "def")  # convert method from async to sync
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

        def modified_test(self):
            with self.subTest(version="sync"):
                client = DEV_JSON_RPC_CLIENT if dev else JSON_RPC_CLIENT
                try:
                    exec(
                        sync_code,
                        all_modules,
                        {"self": self, "client": client},
                    )
                except Exception as e:
                    print(sync_code)  # for ease of debugging, since there's no codefile
                    raise e
                # NOTE: passing `globals()` into `exec` is really bad practice and not
                # safe at all, but in this case it's fine because it's only running
                # test code
            with self.subTest(version="async"):
                client = DEV_ASYNC_JSON_RPC_CLIENT if dev else ASYNC_JSON_RPC_CLIENT
                asyncio.run(test_function(self, client))

        return modified_test

    return decorator


def _get_non_decorator_code(function):
    code_lines = inspect.getsourcelines(function)[0]
    line = 0
    while line < len(code_lines):
        if "def " in code_lines[line]:
            return code_lines[line:]
        line += 1


def retry(test_function):
    NUM_RETRIES = 10

    def modified_test(self):
        for i in range(NUM_RETRIES):
            try:
                test_function(self)
            except Exception:
                if i == NUM_RETRIES - 1:
                    raise
                sleep(2)

    return modified_test
