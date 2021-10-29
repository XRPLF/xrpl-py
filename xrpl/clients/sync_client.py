"""Interface for all sync network clients to follow."""
from __future__ import annotations

import asyncio
from typing import Dict, Union

from xrpl.account import main as account_methods
from xrpl.asyncio.clients.client import Client
from xrpl.asyncio.ledger import main as ledger_methods
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


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
        """
        Query the ledger for whether the account exists.

        Args:
            address: the account to query.

        Returns:
            Whether the account exists on the ledger.

        Raises:
            XRPLRequestFailureException: if the transaction fails.
        """
        return account_methods.does_account_exist(address, self)

    def get_next_valid_seq_number(self: SyncClient, address: str) -> int:
        """
        Query the ledger for the next available sequence number for an account.

        Args:
            address: the account to query.

        Returns:
            The next valid sequence number for the address.
        """
        return account_methods.get_next_valid_seq_number(address, self)

    def get_balance(self: SyncClient, address: str) -> int:
        """
        Query the ledger for the balance of the given account.

        Args:
            address: the account to query.

        Returns:
            The balance of the address.
        """
        return account_methods.get_balance(address, self)

    def get_account_root(self: SyncClient, address: str) -> Dict[str, Union[int, str]]:
        """
        Query the ledger for the AccountRoot object associated with a given address.

        Args:
            address: the account to query.

        Returns:
            The AccountRoot dictionary for the address.
        """
        return account_methods.get_account_root(address, self)

    def get_account_info(self: SyncClient, address: str) -> Response:
        """
        Query the ledger for account info of given address.

        Args:
            address: the account to query.

        Returns:
            The account info for the address.

        Raises:
            XRPLRequestFailureException: if the rippled API call fails.
        """
        return account_methods.get_account_info(address, self)

    """
    Ledger methods.
    """

    def get_latest_validated_ledger_sequence(self: SyncClient) -> int:
        """
        Returns the sequence number of the latest validated ledger.

        Returns:
            The sequence number of the latest validated ledger.

        Raises:
            XRPLRequestFailureException: if the rippled API call fails.
        """
        return asyncio.run(ledger_methods.get_latest_validated_ledger_sequence(self))

    def get_latest_open_ledger_sequence(self: SyncClient) -> int:
        """
        Returns the sequence number of the latest open ledger.

        Returns:
            The sequence number of the latest open ledger.

        Raises:
            XRPLRequestFailureException: if the rippled API call fails.
        """
        return asyncio.run(ledger_methods.get_latest_open_ledger_sequence(self))

    def get_fee(self: SyncClient) -> str:
        """
        Query the ledger for the current minimum transaction fee.

        Returns:
            The minimum fee for transactions.

        Raises:
            XRPLRequestFailureException: if the rippled API call fails.
        """
        return asyncio.run(ledger_methods.get_fee(self))
