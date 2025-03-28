"""Utility functions and variables for integration tests."""

import asyncio
import importlib
import inspect
from threading import Timer as ThreadingTimer
from time import sleep
from typing import Any, Dict, cast

import xrpl  # noqa: F401 - needed for sync tests
from xrpl.asyncio.clients import AsyncJsonRpcClient, AsyncWebsocketClient
from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.asyncio.transaction import sign_and_submit as sign_and_submit_async
from xrpl.clients import Client, JsonRpcClient, WebsocketClient
from xrpl.clients.sync_client import SyncClient
from xrpl.constants import CryptoAlgorithm
from xrpl.models import GenericRequest, Payment, Request, Response, Transaction
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.currencies.xrp import XRP
from xrpl.models.requests import Ledger
from xrpl.models.transactions.account_set import AccountSet, AccountSetAsfFlag
from xrpl.models.transactions.amm_create import AMMCreate
from xrpl.models.transactions.oracle_set import OracleSet
from xrpl.models.transactions.trust_set import TrustSet, TrustSetFlag
from xrpl.transaction import sign_and_submit  # noqa: F401 - needed for sync tests
from xrpl.transaction import (  # noqa: F401 - needed for sync tests
    submit as submit_transaction_alias,
)
from xrpl.utils import ripple_time_to_posix
from xrpl.wallet import Wallet

JSON_RPC_URL = "http://127.0.0.1:5005"
WEBSOCKET_URL = "ws://127.0.0.1:6006"

JSON_TESTNET_URL = "https://s.altnet.rippletest.net:51234"
WEBSOCKET_TESTNET_URL = "wss://s.altnet.rippletest.net:51233"

JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)
ASYNC_JSON_RPC_CLIENT = AsyncJsonRpcClient(JSON_RPC_URL)

WEBSOCKET_CLIENT = WebsocketClient(WEBSOCKET_URL)
ASYNC_WEBSOCKET_CLIENT = AsyncWebsocketClient(WEBSOCKET_URL)

JSON_RPC_TESTNET_CLIENT = JsonRpcClient(JSON_TESTNET_URL)
ASYNC_JSON_RPC_TESTNET_CLIENT = AsyncJsonRpcClient(JSON_TESTNET_URL)

WEBSOCKET_TESTNET_CLIENT = WebsocketClient(WEBSOCKET_TESTNET_URL)
ASYNC_WEBSOCKET_TESTNET_CLIENT = AsyncWebsocketClient(WEBSOCKET_TESTNET_URL)

# (is_async, is_json, is_testnet) -> client
_CLIENTS = {
    (True, True, True): ASYNC_JSON_RPC_TESTNET_CLIENT,
    (True, True, False): ASYNC_JSON_RPC_CLIENT,
    (True, False, True): ASYNC_WEBSOCKET_TESTNET_CLIENT,
    (True, False, False): ASYNC_WEBSOCKET_CLIENT,
    (False, True, True): JSON_RPC_TESTNET_CLIENT,
    (False, True, False): JSON_RPC_CLIENT,
    (False, False, True): WEBSOCKET_TESTNET_CLIENT,
    (False, False, False): WEBSOCKET_CLIENT,
}

MASTER_ACCOUNT = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
MASTER_SECRET = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
MASTER_WALLET = Wallet.from_seed(MASTER_SECRET, algorithm=CryptoAlgorithm.SECP256K1)
FUNDING_AMOUNT = "2000000000"

LEDGER_ACCEPT_REQUEST = GenericRequest(method="ledger_accept")
LEDGER_ACCEPT_TIME = 0.1


class AsyncTestTimer:
    def __init__(
        self,
        client: AsyncClient,
        delay: float = LEDGER_ACCEPT_TIME,
        request: Request = LEDGER_ACCEPT_REQUEST,
    ):
        self._client = client
        self._delay = delay
        self._request = request
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._delay)
        await self._client.request(self._request)

    def cancel(self):
        self._task.cancel()


class SyncTestTimer:
    def __init__(
        self,
        client: SyncClient,
        delay: float = LEDGER_ACCEPT_TIME,
        request: Request = LEDGER_ACCEPT_REQUEST,
    ):
        self._timer = ThreadingTimer(delay, client.request, (request,))
        self._timer.start()

    def cancel(self):
        self._timer.cancel()


def fund_wallet(wallet: Wallet) -> None:
    client = JSON_RPC_CLIENT
    payment = Payment(
        account=MASTER_ACCOUNT,
        destination=wallet.address,
        amount=FUNDING_AMOUNT,
    )
    sign_and_submit(payment, client, MASTER_WALLET, check_fee=True)
    client.request(LEDGER_ACCEPT_REQUEST)


async def fund_wallet_async(
    wallet: Wallet, client: AsyncClient = ASYNC_JSON_RPC_CLIENT
) -> None:
    payment = Payment(
        account=MASTER_ACCOUNT,
        destination=wallet.address,
        amount=FUNDING_AMOUNT,
    )
    await sign_and_submit_async(payment, client, MASTER_WALLET, check_fee=True)
    await client.request(LEDGER_ACCEPT_REQUEST)


# just submits a transaction to the ledger, synchronously
def submit_transaction(
    transaction: Transaction,
    wallet: Wallet,
    client: SyncClient,
    check_fee: bool = True,
) -> Response:
    """Signs and submits a transaction to the XRPL."""
    return sign_and_submit(transaction, client, wallet, check_fee=check_fee)


# just submits a transaction to the ledger, asynchronously
async def submit_transaction_async(
    transaction: Transaction,
    wallet: Wallet,
    client: AsyncClient,
    check_fee: bool = True,
) -> Response:
    return await sign_and_submit_async(transaction, client, wallet, check_fee=check_fee)


# submits a transaction to the ledger and closes a ledger, synchronously
def sign_and_reliable_submission(
    transaction: Transaction,
    wallet: Wallet,
    client: SyncClient = JSON_RPC_CLIENT,
    check_fee: bool = True,
) -> Response:
    modified_transaction = transaction

    # OracleSet transaction needs to set a field within a lower-bound
    # of the last ledger close time. This is a workaround to ensure that such
    # transactions do not fail with tecINVALID_UPDATE_TIME error
    if isinstance(transaction, OracleSet):
        transaction_json = transaction.to_dict()

        # Fetch the last ledger close time
        last_validated_ledger = client.request(Ledger(ledger_index="validated"))

        # Use the last validated ledger close time as the last_update_time
        # The local system clock is not synchronized with standalone rippled node.
        # Empirical observations display a difference of ~1200 seconds between the two.
        # Note: The cause of this discrepancy is the LEDGER_ACCEPT_TIME parameter set
        # to 0.1 seconds. Further investigation is required toward future updates to
        # this parameter.
        transaction_json["last_update_time"] = ripple_time_to_posix(
            last_validated_ledger.result["ledger"]["close_time"]
        )

        modified_transaction = Transaction.from_dict(transaction_json)

    response = submit_transaction(
        modified_transaction, wallet, client, check_fee=check_fee
    )
    client.request(LEDGER_ACCEPT_REQUEST)
    return response


# submits a transaction to the ledger and closes a ledger, asynchronously
async def sign_and_reliable_submission_async(
    transaction: Transaction,
    wallet: Wallet,
    client: AsyncClient = ASYNC_JSON_RPC_CLIENT,
    check_fee: bool = True,
) -> Response:
    modified_transaction = transaction

    # OracleSet transaction needs to set a field within a lower-bound
    # of the last ledger close time. This is a workaround to ensure that such
    # transactions do not fail with tecINVALID_UPDATE_TIME error
    if isinstance(transaction, OracleSet):
        transaction_json = transaction.to_dict()

        # Fetch the last ledger close time
        last_validated_ledger = await client.request(Ledger(ledger_index="validated"))

        # Use the last validated ledger close time as the last_update_time
        # The local system clock is not synchronized with standalone rippled node.
        # Empirical observations display a difference of ~1200 seconds between the two.
        # Note: The cause of this discrepancy is the LEDGER_ACCEPT_TIME parameter set
        # to 0.1 seconds. Further investigation is required toward future updates to
        # this parameter.
        transaction_json["last_update_time"] = ripple_time_to_posix(
            last_validated_ledger.result["ledger"]["close_time"]
        )
        modified_transaction = Transaction.from_dict(transaction_json)

    response = await submit_transaction_async(
        modified_transaction, wallet, client, check_fee=check_fee
    )
    await client.request(LEDGER_ACCEPT_REQUEST)
    return response


def accept_ledger(
    use_json_client: bool = True, delay: float = LEDGER_ACCEPT_TIME
) -> None:
    """
    Allows integration tests for sync clients to send a `ledger_accept` request
    after a set period of time.

    Arguments:
        use_json_client: boolean for choosing json or websocket client.
        delay: float for how many seconds to wait before accepting ledger.
    """
    client = _choose_client(use_json_client)
    SyncTestTimer(client, delay)


async def accept_ledger_async(
    use_json_client: bool = True, delay: float = LEDGER_ACCEPT_TIME
) -> None:
    """
    Allows integration tests for async clients to send a `ledger_accept` request
    after a set period of time.

    Arguments:
        use_json_client: boolean for choosing json or websocket client.
        delay: float for how many seconds to wait before accepting ledger.
    """
    client = _choose_client_async(use_json_client)
    AsyncTestTimer(client, delay)


def _choose_client(use_json_client: bool) -> SyncClient:
    return cast(SyncClient, _CLIENTS[(False, use_json_client, False)])


def _choose_client_async(use_json_client: bool) -> AsyncClient:
    return cast(AsyncClient, _CLIENTS[(True, use_json_client, False)])


def _get_client(is_async: bool, is_json: bool, is_testnet: bool) -> Client:
    return _CLIENTS[(is_async, is_json, is_testnet)]


def test_async_and_sync(
    original_globals,
    modules=None,
    websockets_only=False,
    num_retries=1,
    use_testnet=False,
    async_only=False,
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

        if not async_only:
            sync_modules_to_import = {}
            if modules is not None:
                for module_str in modules:
                    function = module_str.split(".")[-1]
                    location = module_str[: -1 * len(function) - 1]
                    module = getattr(importlib.import_module(location), function)
                    sync_modules_to_import[function] = module

            all_modules = {**original_globals, **globals(), **sync_modules_to_import}
        else:
            all_modules = {**original_globals, **globals()}
        # NOTE: passing `globals()` into `exec` is really bad practice and not safe at
        # all, but in this case it's fine because it's only running test code

        def _run_sync_test(self, client, value):
            self.value = value
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

        async def _run_async_test(self, client, value):
            self.value = value
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
                    asyncio.run(
                        _run_async_test(self, _get_client(True, True, use_testnet), 1)
                    )
                if not async_only:
                    with self.subTest(version="sync", client="json"):
                        _run_sync_test(self, _get_client(False, True, use_testnet), 2)
            with self.subTest(version="async", client="websocket"):
                asyncio.run(
                    _run_async_test(self, _get_client(True, False, use_testnet), 3)
                )
            if not async_only:
                with self.subTest(version="sync", client="websocket"):
                    _run_sync_test(self, _get_client(False, False, use_testnet), 4)

        return modified_test

    return decorator


def _get_non_decorator_code(function):
    code_lines = inspect.getsourcelines(function)[0]
    line = 0
    while line < len(code_lines):
        if "def " in code_lines[line]:
            return code_lines[line:]
        line += 1


def create_amm_pool(
    client: SyncClient = JSON_RPC_CLIENT,
    enable_amm_clawback: bool = False,
) -> Dict[str, Any]:
    issuer_wallet = Wallet.create()
    fund_wallet(issuer_wallet)
    lp_wallet = Wallet.create()
    fund_wallet(lp_wallet)
    currency_code = "USD"

    # test prerequisites - create trustline and send funds
    sign_and_reliable_submission(
        AccountSet(
            account=issuer_wallet.classic_address,
            set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE,
        ),
        issuer_wallet,
    )

    # The below flag is required for AMMClawback tests
    if enable_amm_clawback:
        sign_and_reliable_submission(
            AccountSet(
                account=issuer_wallet.classic_address,
                set_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
            ),
            issuer_wallet,
        )

    sign_and_reliable_submission(
        TrustSet(
            account=lp_wallet.classic_address,
            flags=TrustSetFlag.TF_CLEAR_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer_wallet.classic_address,
                currency=currency_code,
                value="1000",
            ),
        ),
        lp_wallet,
    )

    sign_and_reliable_submission(
        Payment(
            account=issuer_wallet.classic_address,
            destination=lp_wallet.classic_address,
            amount=IssuedCurrencyAmount(
                currency=currency_code,
                issuer=issuer_wallet.classic_address,
                value="500",
            ),
        ),
        issuer_wallet,
    )

    sign_and_reliable_submission(
        AMMCreate(
            account=lp_wallet.classic_address,
            amount="250",
            amount2=IssuedCurrencyAmount(
                issuer=issuer_wallet.classic_address,
                currency=currency_code,
                value="250",
            ),
            trading_fee=12,
        ),
        lp_wallet,
        client,
    )

    asset = XRP()
    asset2 = IssuedCurrency(
        currency=currency_code,
        issuer=issuer_wallet.classic_address,
    )

    return {
        "asset": asset,
        "asset2": asset2,
        "issuer_wallet": issuer_wallet,
        "lp_wallet": lp_wallet,
    }


async def create_amm_pool_async(
    client: AsyncClient = ASYNC_JSON_RPC_CLIENT,
    enable_amm_clawback: bool = False,
) -> Dict[str, Any]:
    issuer_wallet = Wallet.create()
    await fund_wallet_async(issuer_wallet)
    lp_wallet = Wallet.create()
    await fund_wallet_async(lp_wallet)
    currency_code = "USD"

    # test prerequisites - create trustline and send funds
    await sign_and_reliable_submission_async(
        AccountSet(
            account=issuer_wallet.classic_address,
            set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE,
        ),
        issuer_wallet,
    )

    # The below flag is required for AMMClawback tests
    if enable_amm_clawback:
        await sign_and_reliable_submission_async(
            AccountSet(
                account=issuer_wallet.classic_address,
                set_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
            ),
            issuer_wallet,
        )

    await sign_and_reliable_submission_async(
        TrustSet(
            account=lp_wallet.classic_address,
            flags=TrustSetFlag.TF_CLEAR_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer_wallet.classic_address,
                currency=currency_code,
                value="1000",
            ),
        ),
        lp_wallet,
    )

    await sign_and_reliable_submission_async(
        Payment(
            account=issuer_wallet.classic_address,
            destination=lp_wallet.classic_address,
            amount=IssuedCurrencyAmount(
                currency=currency_code,
                issuer=issuer_wallet.classic_address,
                value="500",
            ),
        ),
        issuer_wallet,
    )

    await sign_and_reliable_submission_async(
        AMMCreate(
            account=lp_wallet.classic_address,
            amount="250",
            amount2=IssuedCurrencyAmount(
                issuer=issuer_wallet.classic_address,
                currency=currency_code,
                value="250",
            ),
            trading_fee=12,
        ),
        lp_wallet,
        client,
    )

    asset = XRP()
    asset2 = IssuedCurrency(
        currency=currency_code,
        issuer=issuer_wallet.classic_address,
    )

    return {
        "asset": asset,
        "asset2": asset2,
        "issuer_wallet": issuer_wallet,
        "lp_wallet": lp_wallet,
    }


def compare_amm_values(val, val2, round_buffer):
    diff = abs(float(val) - float(val2))
    if diff > round_buffer:
        raise ValueError(
            f"Values [{val}, {val2}] with difference {diff} are too far apart "
            f"with round_buffer {round_buffer}"
        )
    return True
