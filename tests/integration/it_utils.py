"""Utility functions and variables for integration tests."""

from unittest import IsolatedAsyncioTestCase

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
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)

WEBSOCKET_URL = "wss://s.altnet.rippletest.net/"
WEBSOCKET_CLIENT = WebsocketClient(WEBSOCKET_URL)


def submit_transaction(
    transaction: Transaction,
    wallet: Wallet,
    use_json_client: bool = True,
    check_fee: bool = True,
) -> Response:
    """Signs and submits a transaction to the XRPL."""
    return safe_sign_and_submit_transaction(
        transaction, wallet, _choose_client(use_json_client), check_fee=check_fee
    )


def sign_and_reliable_submission(
    transaction: Transaction, wallet: Wallet, use_json_client: bool = True
) -> Response:
    client = _choose_client(use_json_client)
    signed_tx = safe_sign_and_autofill_transaction(transaction, wallet, client)
    return send_reliable_submission(signed_tx, client)


def _choose_client(use_json_client: bool) -> Client:
    if use_json_client:
        return JSON_RPC_CLIENT
    else:
        return WEBSOCKET_CLIENT


class IntegrationTestCase(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        super(IntegrationTestCase, cls).setUpClass()
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        print("opening1")
        WEBSOCKET_CLIENT.open()

    @classmethod
    def tearDownClass(cls):
        print("closing1")
        #     WEBSOCKET_CLIENT.close()
        super(IntegrationTestCase, cls).tearDownClass()

    # def setUp(self):
    #     print("opening")
    #     WEBSOCKET_CLIENT.open()

    # def tearDown(self):
    #     print("closing")
    #     WEBSOCKET_CLIENT.close()
