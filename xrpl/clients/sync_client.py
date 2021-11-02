"""Interface for all sync network clients to follow."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Union

from xrpl.asyncio.account import main as account_methods
from xrpl.asyncio.account import transaction_history as account_tx_methods
from xrpl.asyncio.clients.client import Client
from xrpl.asyncio.ledger import main as ledger_methods
from xrpl.asyncio.transaction import ledger as tx_ledger_methods
from xrpl.asyncio.transaction import main as tx_main_methods
from xrpl.asyncio.transaction.reliable_submission import send_reliable_submission
from xrpl.models.requests.request import Request
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.wallet.main import Wallet


class SyncClient(Client):
    """
    Interface for all sync network clients to follow.

    :meta private:
    """

    def request(self: SyncClient, request: Request) -> Response:
        """
        Makes a request with this client and returns the response.

        Arguments:
            request: The Request to send.

        Returns:
            The Response for the given Request.
        """
        return asyncio.run(self.request_impl(request))

    """
    Account methods.
    """

    def does_account_exist(self: SyncClient, address: str) -> bool:
        return asyncio.run(account_methods.does_account_exist(address, self))

    def get_next_valid_seq_number(self: SyncClient, address: str) -> int:
        return asyncio.run(account_methods.get_next_valid_seq_number(address, self))

    def get_balance(self: SyncClient, address: str) -> int:
        return asyncio.run(account_methods.get_balance(address, self))

    def get_account_root(self: SyncClient, address: str) -> Dict[str, Union[int, str]]:
        return asyncio.run(account_methods.get_account_root(address, self))

    def get_account_info(self: SyncClient, address: str) -> Response:
        return asyncio.run(account_methods.get_account_info(address, self))

    def get_latest_transaction(self: SyncClient, address: str) -> Response:
        return asyncio.run(account_tx_methods.get_latest_transaction(address, self))

    def get_account_transactions(
        self: SyncClient, address: str
    ) -> List[Dict[str, Any]]:
        return asyncio.run(account_tx_methods.get_account_transactions(address, self))

    def get_account_payment_transactions(
        self: SyncClient, address: str
    ) -> List[Dict[str, Any]]:
        return asyncio.run(
            account_tx_methods.get_account_payment_transactions(address, self)
        )

    """
    Ledger methods.
    """

    def get_latest_validated_ledger_sequence(self: SyncClient) -> int:
        return asyncio.run(ledger_methods.get_latest_validated_ledger_sequence(self))

    def get_latest_open_ledger_sequence(self: SyncClient) -> int:
        return asyncio.run(ledger_methods.get_latest_open_ledger_sequence(self))

    def get_fee(self: SyncClient) -> str:
        return asyncio.run(ledger_methods.get_fee(self))

    """
    Transaction methods.
    """

    def get_transaction_from_hash(
        self: SyncClient,
        tx_hash: str,
        binary: bool = False,
        min_ledger: Optional[int] = None,
        max_ledger: Optional[int] = None,
    ) -> Response:
        return asyncio.run(
            tx_ledger_methods.get_transaction_from_hash(
                tx_hash, self, binary, min_ledger, max_ledger
            )
        )

    def safe_sign_and_submit_transaction(
        self: SyncClient,
        transaction: Transaction,
        wallet: Wallet,
        autofill: bool = True,
        check_fee: bool = True,
    ) -> Response:
        return asyncio.run(
            tx_main_methods.safe_sign_and_submit_transaction(
                transaction, wallet, self, autofill, check_fee
            )
        )

    def submit_transaction(
        self: SyncClient,
        transaction: Transaction,
    ) -> Response:
        return asyncio.run(tx_main_methods.submit_transaction(transaction, self))

    def safe_sign_and_autofill_transaction(
        self: SyncClient,
        transaction: Transaction,
        wallet: Wallet,
        check_fee: bool = True,
    ) -> Transaction:
        return asyncio.run(
            tx_main_methods.safe_sign_and_autofill_transaction(
                transaction, wallet, self, check_fee
            )
        )

    def send_reliable_submission(
        self: SyncClient, transaction: Transaction
    ) -> Response:
        return asyncio.run(send_reliable_submission(transaction, self))
