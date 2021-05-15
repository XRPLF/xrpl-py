"""Interface for all async network clients to follow."""
from __future__ import annotations

from xrpl.asyncio.clients.client import Client
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class AsyncClient(Client):
    """Interface for all async network clients to follow."""

    async def request(self: AsyncClient, request: Request) -> Response:
        """
        Make a request with an AsyncClient.

        Arguments:
            request: The Request to send.

        Returns:
            The Response for the given Request.
        """
        return await self.request_impl(request)
