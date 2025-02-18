"""A common interface for JsonRpc requests."""

from __future__ import annotations

from json import JSONDecodeError
from typing import Optional

from httpx import AsyncClient
from typing_extensions import Self

from xrpl.asyncio.clients.client import REQUEST_TIMEOUT, Client
from xrpl.asyncio.clients.exceptions import XRPLRequestFailureException
from xrpl.asyncio.clients.utils import json_to_response, request_to_json_rpc
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class JsonRpcBase(Client):
    """
    A common interface for JsonRpc requests.

    :meta private:
    """

    def __init__(self: Self, url: str, api_key: Optional[str] = None) -> None:
        """
        Initializes a new JsonRpcBase client.

        Arguments:
            url: The URL of the XRPL node to connect to.
            api_key: Optional API key for connecting to a private XRPL server.
        """
        super().__init__(url)
        self.api_key = api_key  # Store the API key if provided

    async def _request_impl(
        self: Self, request: Request, *, timeout: float = REQUEST_TIMEOUT
    ) -> Response:
        """
        Base ``_request_impl`` implementation for JSON RPC.

        Arguments:
            request: An object representing information about a rippled request.
            timeout: The duration within which we expect to hear a response from the
            rippled validator.

        Returns:
            The response from the server, as a Response object.

        Raises:
            XRPLRequestFailureException: if response can't be JSON decoded.

        :meta private:
        """
        # Prepare headers, including the API key if it’s available
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers[
                "Authorization"
            ] = f"Bearer {self.api_key}"  # Adjust key name if necessary

        async with AsyncClient(timeout=timeout) as http_client:
            response = await http_client.post(
                self.url,
                json=request_to_json_rpc(request),
                headers=headers,  # Include the headers with the optional API key
            )
            try:
                return json_to_response(response.json())
            except JSONDecodeError:
                raise XRPLRequestFailureException(
                    {
                        "error": response.status_code,
                        "error_message": response.text,
                    }
                )
