"""Interface for all async network clients to follow."""
from __future__ import annotations

from typing import Any, Dict

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

    async def request_json(
        self: AsyncClient, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Makes a request with this client and returns the response.

        Arguments:
            request: The request JSON to send.

        Returns:
            The response JSON for the given request.
        """
        return await self.request_json_impl(request)
