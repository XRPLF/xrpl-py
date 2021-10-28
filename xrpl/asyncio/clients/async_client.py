"""Interface for all async network clients to follow."""
from __future__ import annotations

from typing import Dict, Union

from xrpl.asyncio.account import main
from xrpl.asyncio.clients.client import Client
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


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

    async def does_account_exist(self: AsyncClient, address: str) -> bool:
        """
        Query the ledger for whether the account exists.

        Args:
            address: the account to query.

        Returns:
            Whether the account exists on the ledger.

        Raises:
            XRPLRequestFailureException: if the transaction fails.
        """
        return await main.does_account_exist(address, self)

    async def get_next_valid_seq_number(self: AsyncClient, address: str) -> int:
        """
        Query the ledger for the next available sequence number for an account.

        Args:
            address: the account to query.

        Returns:
            The next valid sequence number for the address.
        """
        return await main.get_next_valid_seq_number(address, self)

    async def get_balance(self: AsyncClient, address: str) -> int:
        """
        Query the ledger for the balance of the given account.

        Args:
            address: the account to query.

        Returns:
            The balance of the address.
        """
        return await main.get_balance(address, self)

    async def get_account_root(
        self: AsyncClient, address: str
    ) -> Dict[str, Union[int, str]]:
        """
        Query the ledger for the AccountRoot object associated with a given address.

        Args:
            address: the account to query.

        Returns:
            The AccountRoot dictionary for the address.
        """
        return await main.get_account_root(address, self)

    async def get_account_info(self: AsyncClient, address: str) -> Response:
        """
        Query the ledger for account info of given address.

        Args:
            address: the account to query.

        Returns:
            The account info for the address.

        Raises:
            XRPLRequestFailureException: if the rippled API call fails.
        """
        return await main.get_account_info(address, self)
