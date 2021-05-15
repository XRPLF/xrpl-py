"""Interface for all sync network clients to follow."""
from __future__ import annotations

import asyncio

from xrpl.asyncio.clients.client import Client
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class SyncClient(Client):
    """Interface for all sync network clients to follow."""

    def request(self: SyncClient, request: Request) -> Response:
        """
        Requests the specified ledger request and returns its result.

        Arguments:
            request: The Request to send.

        Returns:
            The Response for the given Request.
        """
        return asyncio.run(self.request_impl(request))
