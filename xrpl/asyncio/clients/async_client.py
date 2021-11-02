"""Interface for all async network clients to follow."""
from __future__ import annotations

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


class AsyncClient(Client):
    """
    Interface for all async network clients to follow.

    :meta private:
    """

    async def request(self: AsyncClient, request: Request) -> Response:
        """
        Makes a request with this client and returns the response.

        Arguments:
            request: The Request to send.

        Returns:
            The Response for the given Request.
        """
        return await self.request_impl(request)

    """
    Account methods.
    """

    async def does_account_exist(self: AsyncClient, address: str) -> bool:
        return await account_methods.does_account_exist(address, self)

    async def get_next_valid_seq_number(self: AsyncClient, address: str) -> int:
        return await account_methods.get_next_valid_seq_number(address, self)

    async def get_balance(self: AsyncClient, address: str) -> int:
        return await account_methods.get_balance(address, self)

    async def get_account_root(
        self: AsyncClient, address: str
    ) -> Dict[str, Union[int, str]]:
        return await account_methods.get_account_root(address, self)

    async def get_account_info(self: AsyncClient, address: str) -> Response:
        return await account_methods.get_account_info(address, self)

    async def get_latest_transaction(self: AsyncClient, address: str) -> Response:
        return await account_tx_methods.get_latest_transaction(address, self)

    async def get_account_transactions(
        self: AsyncClient, address: str
    ) -> List[Dict[str, Any]]:
        return await account_tx_methods.get_account_transactions(address, self)

    async def get_account_payment_transactions(
        self: AsyncClient, address: str
    ) -> List[Dict[str, Any]]:
        return await account_tx_methods.get_account_payment_transactions(address, self)

    """
    Ledger methods.
    """

    async def get_latest_validated_ledger_sequence(self: AsyncClient) -> int:
        return await ledger_methods.get_latest_validated_ledger_sequence(self)

    async def get_latest_open_ledger_sequence(self: AsyncClient) -> int:
        return await ledger_methods.get_latest_open_ledger_sequence(self)

    async def get_fee(self: AsyncClient) -> str:
        return await ledger_methods.get_fee(self)

    """
    Transaction methods.
    """

    async def get_transaction_from_hash(
        self: AsyncClient,
        tx_hash: str,
        binary: bool = False,
        min_ledger: Optional[int] = None,
        max_ledger: Optional[int] = None,
    ) -> Response:
        return await tx_ledger_methods.get_transaction_from_hash(
            tx_hash, self, binary, min_ledger, max_ledger
        )

    async def safe_sign_and_submit_transaction(
        self: AsyncClient,
        transaction: Transaction,
        wallet: Wallet,
        autofill: bool = True,
        check_fee: bool = True,
    ) -> Response:
        return await tx_main_methods.safe_sign_and_submit_transaction(
            transaction, wallet, self, autofill, check_fee
        )

    async def submit_transaction(
        self: AsyncClient,
        transaction: Transaction,
    ) -> Response:
        return await tx_main_methods.submit_transaction(transaction, self)

    async def safe_sign_and_autofill_transaction(
        self: AsyncClient,
        transaction: Transaction,
        wallet: Wallet,
        check_fee: bool = True,
    ) -> Transaction:
        return await tx_main_methods.safe_sign_and_autofill_transaction(
            transaction, wallet, self, check_fee
        )

    async def send_reliable_submission(
        self: AsyncClient, transaction: Transaction
    ) -> Response:
        return await send_reliable_submission(transaction, self)
