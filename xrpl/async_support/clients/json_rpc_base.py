"""A common interface for JsonRpc requests."""
from __future__ import annotations

import httpx

from xrpl.async_support.clients.client import Client
from xrpl.async_support.clients.utils import json_to_response, request_to_json_rpc
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class JsonRpcBase(Client):
    """A common interface for JsonRpc requests."""

    async def request_impl(self: JsonRpcBase, request: Request) -> Response:
        """
        Asynchronously submit the request represented by the request_object to the
        rippled node specified by this client's URL.

        Arguments:
            request: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.
        """
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                self.url,
                json=request_to_json_rpc(request),
            )
            return json_to_response(response.json())
