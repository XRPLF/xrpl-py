"""Interface for all sync network clients to follow."""
from __future__ import annotations

import asyncio
from typing import Dict, Union

from xrpl.account import main
from xrpl.asyncio.clients.client import Client
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
        return main.does_account_exist(address, self)

    def get_next_valid_seq_number(self: SyncClient, address: str) -> int:
        """
        Query the ledger for the next available sequence number for an account.

        Args:
            address: the account to query.

        Returns:
            The next valid sequence number for the address.
        """
        return main.get_next_valid_seq_number(address, self)

    def get_balance(self: SyncClient, address: str) -> int:
        """
        Query the ledger for the balance of the given account.

        Args:
            address: the account to query.

        Returns:
            The balance of the address.
        """
        return main.get_balance(address, self)

    def get_account_root(self: SyncClient, address: str) -> Dict[str, Union[int, str]]:
        """
        Query the ledger for the AccountRoot object associated with a given address.

        Args:
            address: the account to query.

        Returns:
            The AccountRoot dictionary for the address.
        """
        return main.get_account_root(address, self)

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
        return main.get_account_info(address, self)
