"""A common interface for JsonRpc requests."""
from __future__ import annotations

from httpx import AsyncClient

from xrpl.asyncio.clients.client import Client
from xrpl.asyncio.clients.utils import json_to_response, request_to_json_rpc
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class JsonRpcBase(Client):
    """
    A common interface for JsonRpc requests.

    :meta private:
    """

    def __init__(self: JsonRpcBase, url: str) -> None:
        """
        Initialize this JsonRpcClient.

        Arguments:
            url: The url to which to connect.
        """
        self.url = url

    async def request_impl(self: JsonRpcBase, request: Request) -> Response:
        """
        Asynchronously submit the request represented by the request_object to the
        rippled node specified by this client's URL.

        Arguments:
            request: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.

        :meta private:
        """
        async with AsyncClient(timeout=10.0) as http_client:
            response = await http_client.post(
                self.url,
                json=request_to_json_rpc(request),
            )
            return json_to_response(response.json())
