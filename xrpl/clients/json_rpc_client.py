"""A client for interacting with the rippled JSON RPC."""
from __future__ import annotations

import asyncio

import httpx

from xrpl.clients.client import Client
from xrpl.clients.utils import json_to_response, request_to_json_rpc
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class JsonRpcClient(Client):
    """A client for interacting with the rippled JSON RPC."""

    async def request_async(self: JsonRpcClient, request_object: Request) -> Response:
        """
        Asynchronously submit the request represented by the request_object to the
        rippled node specified by this client's URL.

        Arguments:
            request_object: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                json=request_to_json_rpc(request_object),
            )
            return json_to_response(response.json())

    def request(self: JsonRpcClient, request_object: Request) -> Response:
        """
        Synchronously submit the request represented by the request_object to the
        rippled node specified by this client's URL.

        Arguments:
            request_object: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.
        """
        return asyncio.run(self.request_async(request_object))
