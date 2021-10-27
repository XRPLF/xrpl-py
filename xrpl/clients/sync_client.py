"""Interface for all sync network clients to follow."""
from __future__ import annotations

import asyncio

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

    def get_balance(self: SyncClient, address: str) -> int:
        """
        Query the ledger for the balance of the given account.

        Args:
            address: the account to query.

        Returns:
            The balance of the address.
        """
        return main.get_balance(address, self)
